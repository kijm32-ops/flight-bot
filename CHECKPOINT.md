# Checkpoint

## Status

- Current state: V1.3 FOCUS SEARCH IMPLEMENTED ON FEATURE BRANCH; VALIDATION PENDING
- Current task: PTIS v1.3 Focus Search
- Base: latest `main` after v1.2 hardening
- Feature branch: `ptis-v1.3-focus-search`
- Net scheduled SerpAPI usage added by v1.3: 0 calls/month

## v1.3 Implemented

- Added `user_config.json` with Focus Search disabled by default.
- Added `focus.py` for validation, expiration handling, date-window clamping,
  query construction, request parameters, and post-normalization matching.
- Focus Search supports region, origin, outbound date window, optional stay range,
  and optional max price.
- Stay range is encoded in the Deals API `query`; `trip_length` is never sent
  with `query`.
- Active Focus replaces `GMP/near` at the same seventh daily priority position.
- Expired/invalid/disabled Focus restores the original discovery task.
- Focus results reuse existing normalization and safety gates but stay outside
  discovery carryover, quota/diversity, and exposure logic.
- Kakao prioritizes Focus results when present.
- GitHub Pages renders a separate Focus section above discovery results.
- Existing email delivery receives Focus results first without changing its public
  function contract for callers that do not use Focus.
- Added focused unit tests and README configuration instructions.

## Budget

- Existing schedule: 7 daily tasks x 31 days = 217 calls.
- Weekly deep search: about 4.3 calls/month.
- Expected total remains about 221 calls/month.
- Focus is a replacement slot, not an eighth daily call.

## Validation

Pending pull-request CI:

- Python compile
- full unit tests
- workflow YAML parse
- diff whitespace check
- no real SerpAPI call

## Remaining Work

1. Open v1.3 pull request and inspect **Validate PTIS**.
2. Fix only Focus-related failures if CI is not green.
3. Merge v1.3 after validation.
4. Review the next scheduled daily run for regression.
5. Start v1.4 separately: exact city/airport route watch with the
   `google_flights` engine and no increase to the one-daily-Focus-slot budget.

## Known Risks

- Deals API region queries are natural-language matching and may still return a
  wider destination set than an exact airport watch.
- Existing PTIS normalization/tier caps can reject a Focus result even if it is
  below the user's Focus max_price; this is intentional in v1.3 so safety/value
  gates remain consistent.
- `user_config.json` is manual configuration in v1.3; installer editing can be
  considered later if real-user setup shows that it is needed.

## Resume Point

Run v1.3 PR validation. If green, merge and then begin v1.4 exact route watch as a
separate task/commit.
