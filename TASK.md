# PTIS v1.10.3 China trip settings

## Objective

Add China to the guided GitHub Issue Form without changing search scheduling,
pricing, or existing validation rules.

## Verified baseline

- `main` and `origin/main` were equal at `8da6ca6` before the change.
- `AGENTS.md` and `PROJECT_GUIDE.md` are absent.
- Focus Search accepts a nonempty region string and builds a Deals `query`.
- Route Watch requires a three-letter airport code and builds `arrival_id`.
- The valuation table already maps PVG, PEK, PKX, XIY, and TAO to China tiers.

## Changes

- Add `중국 전체 (China)` for region searches.
- Add Shanghai PVG, Beijing Capital PEK, Beijing Daxing PKX, Xi'an XIY,
  and Qingdao TAO as separate exact-route choices.
- Add configuration tests and document the choices.
- Bump `PTIS_VERSION` from 1.10.2 to 1.10.3.

## Constraints

- Preserve `user_config.json` and `data/state.json`.
- Make no SerpAPI request or scheduling/price-rule change.
- Actual SerpAPI quality for country query `China` remains unverified.

## Validation

- `python -m compileall -q .` passed.
- `python -m unittest test_manage_trip_settings test_focus test_route_watch`: 51 passed before the final form-presence test.
- `python -m unittest -q`: 94 passed after the final test.
- Parsed 8 GitHub YAML files with PyYAML.
