# PTIS v1.9 Choice-based Mobile Trip Settings

## Objective

Let a non-technical user configure Focus Search and Route Watches from a phone
primarily through choices, without typing codes, names, dates, or prices.

## Scope

- Replace common free-text inputs with destination, relative-month, departure-week,
  stay, and budget choices.
- Generate a readable name and valid dates automatically, while retaining
  optional custom destination/date overrides.
- Support adding/replacing an exact route, setting a region/date-range focus, and
  pausing all interest searches.
- Validate and atomically update `user_config.json` with a tested Python command.
- Link the form from GitHub Pages and the Kakao daily card.
- Include the new managed files in clean-template and updater distribution.
- Preserve Discovery, valuation, selection, state, and the v1.7 one-slot scheduler.
- Do not edit `data/state.json` or call SerpAPI.

## Usage Estimate

- SerpAPI: 0 implementation/test calls and 0 net scheduled calls after deployment.
- GitHub Actions: one short configuration run per user save.
- Expected session: 5 source/workflow/document files plus focused tests.

## Validation

- Python compile and full unit suite.
- Focused guided-date, choice parsing, add/replace/focus/pause, and invalid-input tests.
- Every workflow YAML parsed.
- Clean template build and updater manifest coverage.
- Existing `main` import smoke check and `git diff --check`.

## Completion Criteria

- The user can save a common trip by making choices only.
- Optional custom fields still support destinations and dates outside the presets.
- Invalid dates, airport codes, stays, and prices do not change the config file.
- Existing settings are preserved unless the chosen operation explicitly replaces
  or pauses them.
- The next scheduled PTIS run reads the saved configuration automatically.
