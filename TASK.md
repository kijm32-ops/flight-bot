# PTIS v1.3 Focus Search

## Objective

Add one daily user-intent Focus Search for a region/date window while preserving
the existing Discovery Search behavior and monthly SerpAPI budget.

## Background

The discovery profiles intentionally search broad date and price windows. They are
good at finding unexpected discounts but can feel random when the user already
knows the region and travel window they care about.

SerpAPI's current `google_flights_deals` API supports `query`,
`outbound_date` ranges, and `max_price`. It does not allow `query` and
`trip_length` together, so v1.3 expresses an optional stay range inside the query
text instead of sending `trip_length`.

## Scope

- Add `user_config.json` as the single source for user Focus preferences.
- Support enabled/origin/region/outbound_from/outbound_to plus optional
  stay_min/stay_max and max_price.
- Validate settings and disable only Focus when settings are invalid or expired.
- Replace the low-priority daily `GMP/near` task with one Focus task when active.
- Keep the Saturday `ICN/deep` task and all other discovery priorities unchanged.
- Reuse existing normalization and price-safety gates for Focus results.
- Keep Focus results out of discovery carryover, quota/diversity, and exposure
  demotion.
- Show Focus results first in Kakao and in a separate GitHub Pages section.
- Keep exact city/airport route watching out of this version.

## Budget

- Focus OFF: 7 daily tasks + weekly deep, unchanged.
- Focus ON: 6 original daily discovery tasks + 1 Focus task + weekly deep.
- Expected monthly total remains about 221 calls.
- Net scheduled SerpAPI increase: 0 calls/month.

## Files

- `focus.py`
- `user_config.json`
- `main.py`
- `notifier.py`
- `report_generator.py`
- `test_focus.py`
- `README.md`
- `TASK.md`
- `CHECKPOINT.md`

## Explicit Non-goals

- Do not modify `ACCESS_COST`, `TIER_HARD_CAP`, `TIER_BASELINE`, or
  `TIER_TRIP_DAYS` ownership.
- Do not change discovery carryover/valuation/selection semantics.
- Do not edit `data/state.json`.
- Do not add a new daily API call.
- Do not implement exact route/date watching with the separate
  `google_flights` engine; that is v1.4.

## Validation

- `python -m py_compile *.py`
- `python -m unittest`
- workflow YAML parse
- `git diff --check`
- Focus config valid/invalid/expired tests
- Focus ON/OFF/deep/budget task-shape tests
- mocked SerpAPI parameter-shape test
- Kakao focus-priority test
- Pages focus-section test
- no real SerpAPI call

## Completion Criteria

- Focus ON replaces, rather than adds to, the seventh daily slot.
- Focus OFF or expired restores `GMP/near`.
- Focus failures cannot stop Discovery Search.
- Focus requests never combine `query` with `trip_length`.
- Focus output is visibly separated from discovery output.
- Full validation passes with zero real SerpAPI calls.
