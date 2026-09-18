# PTIS v1.4 Exact Route Watch

## Objective

Add exact airport/date route monitoring with SerpAPI `google_flights` while
preserving the existing single daily user-intent slot and monthly SerpAPI budget.

## Verified API Facts

SerpAPI `google_flights` supports exact `departure_id`, `arrival_id`,
`outbound_date`, `return_date`, `max_price`, and `stops`.

For round trips, the initial response already includes a round-trip ticket
`price` for each outbound option. A second request with `departure_token` is
required only to inspect the return-flight choices. v1.4 is a price/route watch,
so it intentionally uses only the initial request and does not spend a second
SerpAPI call.

## Scope

- Add `route_watch` settings to `user_config.json`.
- Support exact origin airport, destination airport, outbound date, return date,
  optional max price, and optional nonstop-only.
- Parse the initial `google_flights` response and surface the cheapest matching
  round-trip fare as a PTIS `Flight`.
- Keep Route Watch logically separate from discovery carryover/quota/exposure.
- Share the existing daily user-intent slot with v1.3 Focus Search.
- When both Region Focus and Route Watch are active, support deterministic
  `alternate`, `route_first`, or `region_first` slot selection.
- Show Route Watch before Region Focus and Discovery in Kakao and Pages output.
- Keep user configuration failures isolated from the Discovery pipeline.

## Budget

- Only one user-intent task may run per day.
- Focus/Route Watch replaces `GMP/near` one-for-one.
- Saturday `ICN/deep` behavior remains unchanged.
- Expected monthly total remains about 221 calls/month.
- Net scheduled SerpAPI increase: 0 calls/month.
- No `departure_token` follow-up call in v1.4.

## Explicit Non-goals

- Do not fetch return-flight leg details.
- Do not fetch booking options with `booking_token`.
- Do not edit `data/state.json`.
- Do not change discovery valuation/carryover/selection behavior.
- Do not mix installed-user update delivery into this feature branch.

## Validation

- `python -m py_compile *.py`
- `python -m unittest`
- workflow YAML parse
- `git diff --check`
- Route Watch config valid/invalid/expired tests
- exact google_flights request-shape test
- initial-response parser tests
- Focus/Route slot arbitration tests
- budget task-shape tests
- Kakao/Pages route-priority tests
- no real SerpAPI call

## Completion Criteria

- Exact route/date watch uses exactly one planned SerpAPI task.
- No `departure_token` request is made.
- Focus and Route Watch never consume two daily slots together.
- Invalid/expired watch restores either Region Focus or `GMP/near` as appropriate.
- Full validation passes with zero real SerpAPI calls.
