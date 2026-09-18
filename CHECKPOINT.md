# Checkpoint

## Status

- Current state: V1.4 EXACT ROUTE WATCH IMPLEMENTED ON FEATURE BRANCH; VALIDATION PENDING
- Current task: PTIS v1.4 Exact Route Watch
- Feature branch: `ptis-v1.4-route-watch`
- Base: latest `main` after v1.3 Focus Search
- Net scheduled SerpAPI usage added by v1.4: 0 calls/month

## v1.4 Implemented

- Added `route_watch.py` for exact airport/date configuration, validation,
  expiration handling, single-slot arbitration, and initial response parsing.
- Route Watch supports:
  - origin airport
  - destination airport
  - exact outbound date
  - exact return date
  - optional max price
  - optional nonstop-only
- Added `search.fetch_google_flights()` for one exact `google_flights` request.
- No `departure_token` or `booking_token` follow-up request is made in v1.4.
- Added `focus_slot.mode`:
  - `alternate`
  - `route_first`
  - `region_first`
- v1.3 Region Focus and v1.4 Route Watch share the same one-daily user-intent slot.
- That slot still replaces `GMP/near`; no eighth daily call is added.
- Route Watch output is logically separate from Discovery carryover/quota/exposure.
- Kakao output priority: Route Watch -> Region Focus -> Discovery.
- Pages output priority: Route Watch -> Region Focus -> Discovery.
- Added focused Route Watch tests and README configuration instructions.
- `data/state.json` and discovery valuation/carryover/selection semantics were not changed.

## Budget

- 7 daily tasks x 31 days = 217 calls.
- Weekly deep search adds about 4.3 calls/month.
- Expected monthly total remains about 221 calls/month.
- Safety budget remains 235 calls/month.
- Route Watch shares the existing Focus replacement slot.
- No return-leg detail request is made, so a Route Watch day plans one user-intent
  SerpAPI call, not two.

## Validation

Pending pull-request CI:

- Python compile
- full unit tests
- workflow YAML parse
- `git diff --check`
- no real SerpAPI call

## Remaining Work

1. Open v1.4 pull request and inspect **Validate PTIS**.
2. Fix only v1.4-related failures if CI is not green.
3. Merge v1.4 after validation.
4. Review the next scheduled daily run for regression.
5. After v1.4 is stable, implement the deferred installed-user update path as a
   separate task/branch:
   - clean distribution/template source
   - version source of truth
   - installed repository update detection
   - user-approved update PR
   - preserve runtime/auth/user-config/secrets

## Known Risks

- v1.4 intentionally reads only the initial `google_flights` response; it does
  not enumerate the return-leg choices behind `departure_token`.
- `google_flights` initial flight entries and Deals API entries have different
  schemas; Route Watch therefore has a separate parser.
- Exact airport codes are required in v1.4; city aliases and multiple-airport city
  groups are not supported.
- Update delivery to already-installed third-party repositories remains deferred
  until after this feature is merged.

## Resume Point

Run v1.4 PR validation. If green, merge. Then create a separate distribution/update
task instead of mixing updater mechanics into the Route Watch feature.
