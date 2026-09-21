# PTIS v1.7 Multi Route Watch + User-intent Scheduler

## Objective

Extend Exact Route Watch to multiple routes while preserving one shared daily
user-intent SerpAPI slot with Region Focus.

## Scope

- Accept `route_watches` as an ordered list and preserve v1.4 `route_watch`.
- Select one active Focus/Route intent by KST-date deterministic rotation.
- Exclude invalid and expired routes independently.
- Preserve Discovery valuation, carryover, exposure, and selection semantics.
- Show the selected Route Watch label in Pages and Kakao.
- Bump `PTIS_VERSION` to `1.7.0` and verify template/updater compatibility.

## Do Not Change

- `data/state.json`.
- Discovery search task count or the monthly API budget.
- Legacy-user bootstrap in `Victoryun0919/flight-bot`.
- Real SerpAPI execution.

## Validation

- [x] Python compile
- [x] Full unit suite including multi-route scheduler coverage
- [x] Workflow YAML parse
- [x] `git diff --check`
- [x] Clean template build
- [x] No real SerpAPI call

## Completion Criteria

- One active intent replaces exactly one `GMP/near` discovery task.
- Active intents rotate fairly with no scheduler state storage.
- Existing v1.4 single-route configuration remains valid.
