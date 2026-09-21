# Checkpoint

## Status

- Current state: v1.7 implementation complete locally; PR and CI pending.
- Branch: `feature/v1.7-multi-route-watch`
- PTIS_VERSION: `1.7.0`
- SerpAPI usage added by v1.7: 0 scheduled calls (about 221/month retained).

## Completed

- Added ordered `route_watches` list support while retaining legacy `route_watch`.
- Added KST date-ordinal modulo rotation across Focus and active Route Watches.
- Invalid/expired list entries are skipped without suppressing valid watches.
- Kept the one-for-one `GMP/near` replacement slot and avoided `state.json` changes.
- Added selected Route Watch label to Kakao and Pages output.
- Updated clean-template seed configuration; updater manifest already manages all
  modified program files and leaves `user_config.json` protected/seed-only.

## Validation Performed

- Python compile: passed.
- Full unit suite: passed (72 tests).
- Workflow YAML parse: passed.
- `git diff --check`: passed.
- Clean template build: passed.
- No real SerpAPI call was made; all flight/network tests use mocks.

## Remaining Work

1. Commit, push, open PR, and confirm GitHub Actions CI.
2. Merge after CI succeeds.
3. Synchronize `kijm32-ops/flight-bot-template` from the verified clean artifact;
   do not run legacy-user bootstrap.

## Resume Point

Push `feature/v1.7-multi-route-watch` and create the v1.7 PR.
