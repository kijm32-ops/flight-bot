# PTIS v1.10.1 Focus Search Visibility

## Objective

Make an active Focus Search visibly report its execution status on GitHub Pages and
Kakao even when it returns zero deals.

## Background

Issue #13 successfully saved a Focus Search for CJJ -> Japan, October 2026, 3-5 nights,
with a 300,000 KRW user budget. Subsequent PTIS runs loaded and executed the Focus
Search, but all returned candidates were removed by the existing PTIS price-cap gate.
Because Pages only rendered the Focus section when deals existed and Kakao only
changed its summary when Focus deals existed, the user could not tell that the
configured search had actually run.

Observed 2026-09-24 funnel:

- Focus Search loaded and selected.
- raw=5
- drop_over_cap=5
- qualified=0
- final Focus deals=0

## Scope

- Keep the existing Focus Search query, validation, scheduler, and price gates unchanged.
- Track the Focus-specific funnel separately from the global funnel.
- Build a user-facing Focus label including origin, region, dates, stay, and user budget.
- Build a concise status from the actual Focus funnel.
- Render the Focus section on Pages even when the result count is zero.
- Show the zero-result Focus status in Kakao while preserving existing deal priority.
- Add regression tests for zero-result Pages/Kakao output and funnel status.
- Do not call SerpAPI during implementation or tests.
- Preserve the live protected `user_config.json`; clean-template builds must emit a
  disabled seed instead of copying the owner's active settings.

## Files to Inspect / Change

- `main.py`
- `report_generator.py`
- `notifier.py`
- `test_focus.py`
- `README.md`
- `PTIS_VERSION`
- `build_template.py`
- `test_build_template.py`
- `TASK.md`
- `CHECKPOINT.md`

## Do Not Change

- `data/state.json`
- `user_config.json`
- `TIER_HARD_CAP`
- `ACCESS_COST`
- Discovery selection or carryover logic
- Focus Search API-call count or task scheduling
- SerpAPI monthly budget

## Assumptions Verified

- The current saved Focus Search is enabled and persisted in `user_config.json`.
- The 2026-09-24 scheduled run selected and executed the Focus slot.
- The Focus call returned 5 raw candidates and all 5 were removed by
  `drop_over_cap`.
- Pages currently hides the Focus section when `focus_deals` is empty.
- Kakao currently treats zero Focus deals like no Focus Search was active.

## Validation Blocker Found

The first PR validation run exposed an existing clean-template invariant conflict:
`test_build_template.py` assumed the repository's live `user_config.json` must
always be disabled. That assumption became invalid once the direct settings form
legitimately committed the owner's active Focus Search. Copying the live file into
a clean template would also leak personal trip settings. The minimal safety fix is
to keep `user_config.json` untouched in the repository and have `build_template.py`
emit a disabled default seed only into distribution artifacts.

## Usage Estimate

- SerpAPI implementation/test calls: 0.
- Net scheduled SerpAPI calls after deployment: 0.
- Existing daily seven-task shape remains unchanged.

## Validation

- [x] Python compile passes.
- [x] Full unit suite passes.
- [x] Zero-result Focus status identifies the actual funnel reason.
- [x] Pages renders an active Focus section with zero deals.
- [x] Kakao identifies an active Focus Search with zero deals.
- [x] Positive-result Focus output remains compatible.
- [x] Clean template build passes.
- [x] Pull-request whitespace check passes.
- [x] No real SerpAPI call is made.

## Completion Criteria

- A run with an active Focus Search and zero matching deals is visibly distinguishable
  from a run with no Focus Search configured.
- For the observed funnel, the UI reports that 5 candidates were checked and 5 were
  removed by the PTIS price cap.
- Existing price gates and API budget remain unchanged.
