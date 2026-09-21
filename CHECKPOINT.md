# Checkpoint

## Status

- Current state: v1.9 choice-based mobile settings implemented and validated.
- Branch: `feature/choice-trip-settings`
- Baseline: `13cab95` (v1.8 merged main)
- PTIS_VERSION: `1.9.0`
- SerpAPI usage added: 0 calls; scheduled budget remains about 221/month.

## Completed

- Replaced common text entry with destination, month, departure-week, stay, and
  budget choices.
- Added automatic exact-trip and region-month date generation.
- Kept optional custom destination/date overrides for uncommon trips.
- Added exact-route add/replace, region-focus set, and pause-all operations.
- Added strict validation and atomic `user_config.json` writes.
- Invalid new route input is rejected before the tolerant v1.7 runtime loader can
  skip it silently.
- Added automatic repository-derived settings URL to Pages and Kakao buttons.
- Added the workflow, command, and tests to the updater/template manifest.
- Updated README guidance and bumped version to 1.8.0.
- Preserved Discovery, v1.7 scheduling, and `data/state.json`.

## Changed Files

- Updated: `.github/workflows/trip-settings.yml`, `manage_trip_settings.py`,
  `test_manage_trip_settings.py`, `README.md`, `PTIS_VERSION`, `TASK.md`,
  `CHECKPOINT.md`.
- Unchanged: `data/state.json`, core collection/normalization/valuation/selection.

## Validation Performed

- Python compile: passed.
- Full unit suite: passed, 83 tests.
- Focused mobile-settings suite: passed, 10 tests.
- Workflow YAML parse: passed for every workflow.
- Existing main import smoke: passed.
- New Python source ASCII check: passed.
- `git diff --check`: passed.
- Pages and Kakao settings-button payload tests: passed.
- Clean-template build and required-file presence: passed (rebuild once before handoff).
- No real SerpAPI call was made.

## Remaining Work

1. Commit and push the feature branch, open a PR, confirm CI, and merge.
2. Open the merged `여행 조건 설정` form on a phone and verify the choices.

## Resume Point

Push `feature/choice-trip-settings`, open a PR, and confirm CI.
Do not edit `data/state.json`.
