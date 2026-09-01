import logging
import sys
import concurrent.futures
from collections import Counter
from typing import List, Tuple, Dict
from config import (
    SERPAPI_KEY, BASE_SEARCH_PARAMS, KAKAO_JS_KEY,
    PROFILES, ORIGIN_PROFILES,
    DAILY_TASK_PRIORITY, DEEP_TASK_PRIORITY, is_deep_scan_day,
    SERPAPI_SAFE_BUDGET, SERPAPI_MONTHLY_LIMIT, API_QUOTA_WARNING_THRESHOLD,
)
from search import fetch_raw_flight_deals
from normalizer import normalize_and_deduplicate, collapse_by_destination, format_funnel
from notifier import send_email, send_kakao_message, send_warning_email
from report_generator import generate_report_html
from state import (
    load_state, save_state, update_route_history,
    peek_api_usage, record_api_calls, record_kakao_result,
)
from models import Flight
from origin_compare import annotate_origin_alternatives
from exposure import record_exposure, apply_exposure_penalty
from selection import (
    strict_collapse, apply_caps, sort_by_score, apply_quota, assign_grades,
    TOTAL_SLOTS,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def build_tasks(remaining_budget: int, deep_scan: bool) -> List[Tuple[str, str]]:
    candidates = list(DAILY_TASK_PRIORITY)
    if deep_scan:
        candidates += DEEP_TASK_PRIORITY

    valid = [
        (origin, profile)
        for origin, profile in candidates
        if profile in ORIGIN_PROFILES.get(origin, [])
    ]

    if remaining_budget >= len(valid):
        return valid

    trimmed = valid[:max(0, remaining_budget)]
    dropped = valid[len(trimmed):]
    if dropped:
        logging.warning(
            f"\u26A0\uFE0F \uC608\uC0B0 \uBD80\uC871\uC73C\uB85C {len(dropped)}\uAC1C \uC791\uC5C5 \uC0DD\uB7B5: "
            + ", ".join(f"{o}/{p}" for o, p in dropped)
        )
    return trimmed


def process_profile(origin: str, profile_name: str) -> Tuple[List[Flight], Counter]:
    stats: Counter = Counter()
    try:
        date_range, trip_length = PROFILES[profile_name]
        search_params = {
            **BASE_SEARCH_PARAMS,
            "outbound_date": date_range,
            "trip_length": trip_length,
        }
        raw_deals = fetch_raw_flight_deals(SERPAPI_KEY, search_params, origin)
        if not raw_deals:
            logging.info(f"[{origin} / {profile_name}] no raw deals returned.")
            return [], stats

        flights = normalize_and_deduplicate(origin, raw_deals, stats)
        logging.info(
            f"[{origin} / {profile_name}] {len(flights)} normalized. "
            f"funnel: {format_funnel(stats)}"
        )
        return flights, stats
    except Exception as e:
        logging.error(f"[{origin} / {profile_name}] FAILED: {e}")
        return [], stats


def merge_and_collapse(flights: List[Flight]) -> List[Flight]:
    """
    Merge results from all profiles:
    1) drop exact duplicates (same origin/dest/dates), keeping cheapest
    2) re-collapse per destination so MAX_PER_DESTINATION is enforced globally

    NOTE: this stage is still origin-aware. Cross-origin duplicates
    (GMP/CJJ -> same city) are resolved later in selection.strict_collapse().
    """
    seen: Dict[Tuple[str, str, str, str], Flight] = {}
    for f in flights:
        key = (f.origin, f.destination_name, str(f.depart_date), str(f.return_date))
        if key not in seen or f.price < seen[key].price:
            seen[key] = f

    deduped = list(seen.values())
    before = len(deduped)
    result = collapse_by_destination(deduped)
    logging.info(f"merge: {len(flights)} -> dedup {before} -> collapse {len(result)}")
    return result


def run_system():
    if not SERPAPI_KEY:
        logging.error("SERPAPI_KEY missing.")
        sys.exit(1)

    state = load_state()

    deep_scan = is_deep_scan_day()
    if deep_scan:
        logging.info("Deep scan day (8-11 months ahead included).")

    used = peek_api_usage(state)
    remaining = SERPAPI_SAFE_BUDGET - used
    logging.info(
        f"Budget: {used}/{SERPAPI_MONTHLY_LIMIT} used, "
        f"{remaining} left (safe cap {SERPAPI_SAFE_BUDGET})"
    )

    tasks = build_tasks(remaining, deep_scan)

    if not tasks:
        logging.error("Budget exhausted; skipping API calls.")
        send_warning_email(
            "\U0001F6D1 [PTIS] SerpApi \uC608\uC0B0 \uC18C\uC9C4 \u2014 \uAC80\uC0C9 \uC911\uB2E8",
            f"\uC774\uBC88 \uB2EC SerpApi \uD638\uCD9C\uC774 {used}\uD68C\uC5D0 \uB3C4\uB2EC\uD558\uC5EC "
            f"\uAC80\uC0C9\uC744 \uC911\uB2E8\uD588\uC2B5\uB2C8\uB2E4. "
            f"(\uBB34\uB8CC \uD55C\uB3C4 {SERPAPI_MONTHLY_LIMIT}\uD68C) "
            f"\uB2E4\uC74C \uB2EC 1\uC77C\uC5D0 \uC790\uB3D9\uC73C\uB85C \uC7AC\uAC1C\uB429\uB2C8\uB2E4."
        )
        generate_report_html([], KAKAO_JS_KEY, set())
        save_state(state)
        return

    logging.info(f"Start {len(tasks)} tasks: " + ", ".join(f"{o}/{p}" for o, p in tasks))
    all_final_flights: List[Flight] = []
    funnel: Counter = Counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_to_task = {
            executor.submit(process_profile, origin, profile): (origin, profile)
            for origin, profile in tasks
        }
        for future in concurrent.futures.as_completed(future_to_task):
            origin, profile = future_to_task[future]
            try:
                flights, stats = future.result()
                all_final_flights.extend(flights)
                funnel.update(stats)
            except Exception as exc:
                logging.error(f"[{origin} / {profile}] thread error: {exc}")

    logging.info("FUNNEL (all tasks): " + format_funnel(funnel))

    all_final_flights = merge_and_collapse(all_final_flights)
    all_final_flights = annotate_origin_alternatives(all_final_flights)

    # --- selection pipeline -------------------------------------------------
    # 1) one row per destination, regardless of origin (must run before grading)
    all_final_flights = strict_collapse(all_final_flights)
    # 2) hard ceiling per tier: too expensive to ever book, however big the cut
    all_final_flights = apply_caps(all_final_flights)
    # 3) rank by baseline discount on the access-cost-inclusive price
    all_final_flights = sort_by_score(all_final_flights)
    # 4) demote destinations shown repeatedly in recent days
    all_final_flights = apply_exposure_penalty(state, all_final_flights)
    # 5) tier quota so one category cannot take over the report
    all_final_flights = apply_quota(all_final_flights)
    # 6) grade relative to this run, not against a fixed threshold
    all_final_flights = assign_grades(all_final_flights)
    # ------------------------------------------------------------------------

    logging.info(
        "SLOTS: %d/%d filled. If this is well under 20, the bottleneck is "
        "upstream (raw yield or gates), not the quota.",
        len(all_final_flights), TOTAL_SLOTS,
    )

    record_exposure(state, all_final_flights)

    logging.info(f"Done. {len(all_final_flights)} deals collected.")

    low_price_keys = update_route_history(state, all_final_flights)
    if low_price_keys:
        logging.info(f"30-day lows: {len(low_price_keys)}")

    total_calls = record_api_calls(state, len(tasks))
    logging.info(f"Monthly SerpApi calls: {total_calls}")
    if total_calls >= API_QUOTA_WARNING_THRESHOLD:
        send_warning_email(
            "\u26A0\uFE0F [PTIS] SerpApi \uD55C\uB3C4 \uC784\uBC15",
            f"\uC774\uBC88 \uB2EC SerpApi \uD638\uCD9C\uC774 {total_calls}\uD68C\uB97C "
            f"\uAE30\uB85D\uD588\uC2B5\uB2C8\uB2E4 (\uBB34\uB8CC \uD55C\uB3C4 {SERPAPI_MONTHLY_LIMIT}\uD68C / "
            f"\uC548\uC804 \uC608\uC0B0 {SERPAPI_SAFE_BUDGET}\uD68C)."
        )

    generate_report_html(all_final_flights, KAKAO_JS_KEY, low_price_keys)

    if all_final_flights:
        send_email(all_final_flights, low_price_keys)
        kakao_success = send_kakao_message(all_final_flights)
        need_warning = record_kakao_result(state, kakao_success)
        if need_warning:
            send_warning_email(
                "\u26A0\uFE0F [PTIS] \uCE74\uCE74\uC624\uD1A1 \uBC1C\uC1A1 3\uD68C \uC5F0\uC18D \uC2E4\uD328",
                "\uCE74\uCE74\uC624\uD1A1 \uC54C\uB9BC\uC774 3\uD68C \uC5F0\uC18D \uBC1C\uC1A1\uC5D0 "
                "\uC2E4\uD328\uD588\uC2B5\uB2C8\uB2E4. KAKAO_REFRESH_TOKEN \uB9CC\uB8CC \uAC00\uB2A5\uC131\uC744 "
                "\uD655\uC778\uD574\uC8FC\uC138\uC694."
            )
    else:
        logging.warning("No deals to send.")

    save_state(state)


if __name__ == "__main__":
    run_system()
