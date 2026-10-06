# Checkpoint: China trip settings

## Status

- Baseline: `main` = `origin/main` = `8da6ca6` before edits; working tree clean.
- Current source version: `1.10.3`.
- China guided choices and configuration tests are implemented and validated.

## Completed

- Confirmed existing China tiers and airport mappings in `valuation.py`.
- Confirmed `China` passes the existing Focus parser and reaches the Deals query.
- Confirmed PVG, PEK, PKX, XIY, and TAO pass Route Watch validation and reach
  `arrival_id`; Beijing airports remain separate choices.
- Confirmed Osaka, Japan, and Southeast Asia choice parsing is unchanged.
- Preserved live `user_config.json` and `data/state.json`.
- Added no scheduled calls; expected daily and monthly SerpAPI change is zero.

## Validation

- Python compile: passed (`python -m compileall -q .`).
- Related tests: 51 passed before the final form-presence test.
- Full unit suite: 94 passed after the final test, including clean-template tests.
- GitHub YAML parse: 8 files passed.
- No real SerpAPI call was made.

## Remaining

- The quality of a live country-level `China` Deals search needs separate
  verification if desired; source and unit tests only establish request shape.
