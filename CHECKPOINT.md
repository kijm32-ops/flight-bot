# Checkpoint

## Status

- Current state: V1.3 FOCUS SEARCH MERGED AND VALIDATED
- Current task: next isolated task is PTIS v1.4 Exact Route Watch
- v1.3 merged commit: `1f08e0a1b8c196bac8462312cd512b7edff442e0`
- Pull request: `#2` (`PTIS v1.3: add Focus Search`)
- Validation run: GitHub Actions `35295799958` — success
- Net scheduled SerpAPI usage added by v1.3: 0 calls/month

## v1.3 Completed

- Added `user_config.json` with Focus Search disabled by default.
- Added `focus.py` for configuration validation, expiration handling, date-window
  clamping, query construction, request parameters, and post-normalization matching.
- Focus Search supports:
  - origin
  - region
  - outbound date window
  - optional stay range
  - optional max price
- Stay range is encoded in the Deals API `query`; `trip_length` is never sent
  together with `query`.
- Active Focus replaces the low-priority daily `GMP/near` task one-for-one.
- Disabled, invalid, or expired Focus restores the original `GMP/near` task.
- Saturday `ICN/deep` behavior remains unchanged.
- Focus results reuse existing normalization and safety gates but remain outside
  discovery carryover, quota/diversity, and exposure handling.
- Kakao prioritizes Focus results when present.
- GitHub Pages renders a separate Focus section above discovery results.
- Existing email delivery receives Focus results first.
- Added focused unit tests and README configuration instructions.
- `data/state.json` and core discovery valuation/carryover semantics were not changed.

## Budget

- 7 daily tasks x 31 days = 217 calls.
- Weekly deep search adds about 4.3 calls/month.
- Expected monthly total remains about 221 calls/month.
- Safety budget remains 235 calls/month.
- Focus is a replacement slot, not an additional daily call.

## Validation

GitHub Actions `Validate PTIS` run `35295799958`: passed.

- dependency installation: passed
- Python compile: passed
- full `python -m unittest`: passed (44 tests)
- workflow YAML parse: passed
- `git diff --check`: passed
- no real SerpAPI call was made by validation

The first validation attempt found a report-generator name-shadowing bug. It was
fixed on the feature branch and the second validation run passed fully before merge.

## Remaining Work

1. Review the next scheduled daily workflow after v1.3 merge for regression.
2. Start PTIS v1.4 Exact Route Watch as a separate task.
3. Deferred distribution/update work:
   - create a dedicated clean `flight-bot-template` repository;
   - define a PTIS version/update source of truth;
   - let installed user repositories detect newer PTIS releases;
   - prefer an update PR / user-approved merge path over silent auto-update;
   - preserve `data/state.json`, `data/kakao_auth.json`, `user_config.json`,
     GitHub Secrets, and other installation-specific data during updates;
   - use the first third-party installation as the regression case for the updater.
   This work is intentionally deferred and must not be mixed into v1.4.

## v1.4 Resume Point

Design exact city/airport route monitoring with the separate SerpAPI
`google_flights` engine.

Constraints:

- examples: `ICN -> NRT` with exact outbound/return dates and max price;
- do not add another daily API slot;
- share the single Focus budget slot with v1.3 Focus Search, using explicit
  priority/rotation rather than increasing monthly usage;
- verify the `google_flights` response/round-trip token flow before implementation;
- keep v1.4 separate from the merged v1.3 region-search code.
