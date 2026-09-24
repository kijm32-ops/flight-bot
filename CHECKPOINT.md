# Checkpoint

## Status

- Current state: PTIS v1.10.1 Focus zero-result visibility implemented; PR #14 validation passed before final documentation update.
- Branch: `fix/focus-zero-result-visibility`
- PR: #14
- Baseline: `ca667569`
- PTIS_VERSION: `1.10.1`
- SerpAPI calls added: 0; scheduled daily task count unchanged.

## Completed

- Verified Issue #13 settings are persisted and active:
  - origin `CJJ`
  - region `Japan`
  - 2026-10-01 through 2026-10-31
  - 3-5 nights
  - max user price 300,000 KRW
- Verified the 2026-09-24 scheduled run actually executed Focus Search:
  - raw=5
  - drop_over_cap=5
  - qualified=0
  - final focus=0
- Added a user-facing Focus label with origin, region, date window, stay, and user budget.
- Added Focus-specific funnel status generation without changing existing gates.
- Pages now renders the Focus section even when zero deals remain.
- Kakao now identifies an active zero-result Focus Search and shows the funnel reason.
- Positive-result Focus behavior remains compatible.
- Search exceptions are distinguishable from legitimate zero-result runs.
- Did not change `TIER_HARD_CAP`, `ACCESS_COST`, scheduler shape, or `data/state.json`.
- Did not modify the protected live `user_config.json`.

## Validation Blocker Resolved

The first PR run failed an existing clean-template test because the live
`user_config.json` is now legitimately enabled by the direct settings workflow.
The clean-template builder also would have copied those active personal settings
into a distribution artifact.

Minimal fix applied:

- `build_template.py` now writes a disabled `DEFAULT_USER_CONFIG` only into clean
  template output.
- The live repository `user_config.json` remains untouched.
- `test_build_template.py` validates the generated seed rather than requiring the
  owner's runtime configuration to be disabled.

## Changed Files

- `main.py` — Focus label/status generation and separate Focus funnel tracking.
- `report_generator.py` — zero-result Focus section and status display.
- `notifier.py` — zero-result Focus visibility in Kakao.
- `test_focus.py` — zero-result funnel, Pages, and Kakao regression tests.
- `build_template.py` — sanitize distribution `user_config.json` seed.
- `test_build_template.py` — validate generated safe seed.
- `README.md` — document zero-result visibility.
- `PTIS_VERSION` — 1.10.1.
- `TASK.md`, `CHECKPOINT.md` — task/report state.

## Validation Performed

- PR #14 Validate PTIS run #17: passed before final documentation-only update.
- Python compile: passed.
- Full unit suite: 90 tests passed.
- GitHub YAML parse: passed.
- Clean-template build: passed, 43 files.
- Pull-request whitespace check: passed.
- No real SerpAPI call was made.

## Remaining Work

1. Run final CI after this documentation update.
2. Merge PR #14 if final CI remains green.
3. Observe the next scheduled PTIS message/Page. With the current saved condition
   and a zero-result funnel, it should visibly show the Focus condition and exclusion reason.

## Current Blockers / Known Issues

- Focus Search still obeys existing PTIS hard caps after the user's API max-price
  filter. This task deliberately does not change that policy.
- The Kakao card has limited visible description space; a long condition/status may
  be truncated by the client, while the full details remain visible on Pages.

## Resume Point

Check the final PR #14 Validate PTIS run. If green, merge without changing search
logic. Do not run Daily Flight Deal Scraper merely for validation because that
would consume SerpAPI budget.

## Risks

- User-entered max price and PTIS `TIER_HARD_CAP` remain separate constraints; a
  user budget higher than the PTIS cap can still yield zero Focus results.
- Any future changes to funnel stage names must update the user-facing mapping in
  `main.py`.

## Next Action

Confirm final CI is green and merge PR #14.
