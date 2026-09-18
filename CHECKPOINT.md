# Checkpoint

## Status

- Current state: V1.4 EXACT ROUTE WATCH MERGED AND VALIDATED
- Current task: next isolated task is PTIS v1.5 Installed-user Update Path
- v1.4 merged commit: `755754863c189ccbbaa1540462e5ba01ec9c5f24`
- Pull request: `#3` (`PTIS v1.4: add Exact Route Watch`)
- Validation run: GitHub Actions `35324763250` — success
- Net scheduled SerpAPI usage added by v1.4: 0 calls/month

## v1.4 Completed

- Added exact airport/date Route Watch with the `google_flights` engine.
- Route Watch supports origin, destination, exact outbound/return dates,
  optional max price, and optional nonstop-only.
- The initial `google_flights` response is sufficient for the monitored
  round-trip fare; v1.4 makes no `departure_token` or `booking_token`
  follow-up request.
- Region Focus and Route Watch share the same one-daily user-intent slot.
- Slot modes:
  - `alternate`
  - `route_first`
  - `region_first`
- Disabled/expired/invalid user-intent searches restore another active intent or
  the original `GMP/near` discovery slot.
- Kakao/Pages output priority is Route Watch -> Region Focus -> Discovery.
- Discovery carryover, valuation, selection, exposure, and `data/state.json`
  semantics were not changed.

## Budget

- 7 daily tasks x 31 days = 217 calls.
- Weekly deep search adds about 4.3 calls/month.
- Expected monthly total remains about 221 calls/month.
- Safety budget remains 235 calls/month.
- v1.4 adds 0 net scheduled calls.

## Validation

GitHub Actions `Validate PTIS` run `35324763250`: passed.

- dependency installation: passed
- Python compile: passed
- full unit tests: passed
- workflow YAML parse: passed
- `git diff --check`: passed
- no real SerpAPI call was made by validation

## Remaining Work

1. Review the next scheduled daily workflow after v1.4 merge for regression.
2. Start PTIS v1.5 Installed-user Update Path as a separate task.
3. Create a dedicated clean `flight-bot-template` repository when repository
   creation/admin tooling is available.

## v1.5 Resume Point

Build an update mechanism for repositories that were already installed from PTIS.

Requirements:

- one upstream PTIS version/source of truth;
- detect newer upstream PTIS versions;
- update only centrally managed program files;
- preserve `data/state.json`, `data/kakao_auth.json`, `user_config.json`,
  GitHub Secrets, and other installation-specific state;
- prefer a user-approved update PR over silent auto-update;
- provide a manual/local fallback;
- use `Victoryun0919/flight-bot` as the first real regression target;
- keep the clean-template repository as a separate repository-administration step
  if repository creation is not available.
