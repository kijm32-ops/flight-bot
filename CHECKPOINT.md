# Checkpoint

## Status

- Current state: v1.8 mobile trip settings implemented and locally validated.
- Branch: `feature/mobile-trip-settings`
- Baseline: `78418e8` (v1.7 merged main)
- PTIS_VERSION: `1.8.0`
- SerpAPI usage added: 0 calls; scheduled budget remains about 221/month.

## Completed

- Added a Korean GitHub Actions form designed for phone use.
- Added exact-route add/replace, region-focus set, and pause-all operations.
- Added strict validation and atomic `user_config.json` writes.
- Invalid new route input is rejected before the tolerant v1.7 runtime loader can
  skip it silently.
- Added automatic repository-derived settings URL to Pages and Kakao buttons.
- Added the workflow, command, and tests to the updater/template manifest.
- Updated README guidance and bumped version to 1.8.0.
- Preserved Discovery, v1.7 scheduling, and `data/state.json`.

## Changed Files

- New: `.github/workflows/trip-settings.yml`, `manage_trip_settings.py`,
  `test_manage_trip_settings.py`.
- Updated: `config.py`, `notifier.py`, `report_generator.py`, `README.md`,
  `.ptis/update_manifest.json`, `PTIS_VERSION`, `TASK.md`, `CHECKPOINT.md`.
- Unchanged: `data/state.json`, core collection/normalization/valuation/selection.

## Validation Performed

- Python compile: passed.
- Full unit suite: passed, 80 tests.
- Focused mobile-settings suite: passed, 7 tests.
- Workflow YAML parse: passed for every workflow.
- Existing main import smoke: passed.
- New Python source ASCII check: passed.
- `git diff --check`: passed.
- Pages and Kakao settings-button payload tests: passed.
- Clean-template build and required-file presence: passed (rebuild once before handoff).
- No real SerpAPI call was made.

## Remaining Work

1. Rebuild the final clean-template artifact after the last test/doc changes.
2. Commit and push the feature branch, open a PR, confirm CI, and merge.
3. Run the newly merged `여행 조건 설정` workflow once from a phone.
4. Run the normal daily workflow once to publish Pages with the new button and
   verify the next Kakao message contains the settings button.

## Resume Point

Finish final clean-template/diff checks, then push `feature/mobile-trip-settings`.
Do not edit `data/state.json`.
