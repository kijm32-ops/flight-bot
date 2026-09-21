# Checkpoint

## Status

- Current state: v1.7 merged to upstream main and synchronized to the clean
  template repository.
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
- Full unit suite: passed (73 tests).
- Workflow YAML parse: passed.
- `git diff --check`: passed.
- Clean template build: passed.
- No real SerpAPI call was made; all flight/network tests use mocks.

## Remaining Work

1. Existing personal installations can use the v1.5 updater path to review and
   apply v1.7 managed files.
2. Do not run legacy-user bootstrap in `Victoryun0919/flight-bot` as part of this
   release.

## Resume Point

Begin the next scoped PTIS feature from upstream `main`.

## Merge Evidence

- Source PR #7: merged after `Validate PTIS` passed; merge commit `78418e8`.
- Template PR #2: merged after `Validate PTIS` passed; merge commit `ed1fe26`.
