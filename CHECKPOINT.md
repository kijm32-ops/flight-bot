# Checkpoint

## Status

- Current state: V1.6 CLEAN TEMPLATE REPOSITORY INITIALIZED AND SMOKE-VALIDATED
- Current task: verify GitHub Template repository flag, then legacy-user bootstrap
- v1.6 merged commit: `dba1d068efc526b8eb99d42332bb4b011949d347`
- Pull request: `#5` (`PTIS v1.6: add clean template distribution artifact`)
- Validation run: GitHub Actions `35342347236` — success
- version-correction merge: `5188364f790d4dceba3dc0631e70f20b59a650e1`
- version-correction validation: GitHub Actions `35343157797` — success
- PTIS_VERSION: `1.6.0`
- SerpAPI usage added by v1.6: 0 calls

## v1.6 Completed

- Added `build_template.py` driven by `.ptis/update_manifest.json`.
- Clean output contains only managed files plus seed-if-missing files.
- Protected runtime/auth files are excluded and rejected if they overlap managed output.
- Added deterministic zip generation.
- Added `test_build_template.py` covering:
  - all manifest files present;
  - `data/state.json` absent;
  - `data/kakao_auth.json` absent;
  - safe disabled `user_config.json` present;
  - TASK/CHECKPOINT absent;
  - repeated zip builds byte-identical;
  - output-inside-source refusal.
- Added `.github/workflows/build-template.yml` to build, verify, and upload the
  clean template zip artifact.
- README now documents clean-template distribution.

## Validation

GitHub Actions `Validate PTIS` run `35342347236`: passed.

- Python compile: passed
- full unit tests: passed
- workflow YAML parse: passed
- `git diff --check`: passed
- no real SerpAPI call was made

## Clean Template Repository

`kijm32-ops/flight-bot-template` now exists and has been initialized from the
v1.6 managed-file/seed allowlist.

Verification:

- every managed/seed file checked in the source exists in the template;
- source/template blob SHAs match for all verified files;
- `assets/kakao_card_v1.png` matches the source binary blob;
- `data/state.json` is absent;
- `data/kakao_auth.json` is absent;
- `TASK.md` and `CHECKPOINT.md` are absent;
- default `user_config.json` is present with Focus/Route disabled;
- PTIS_VERSION is `1.6.0`;
- temporary template smoke PR `#1` ran bundled Validate PTIS;
- template validation run `35343822608` passed;
- the temporary smoke PR was closed without merge;
- template README was synchronized after validation (docs-only change).

## Remaining Work

1. Confirm in GitHub repository settings that
   `kijm32-ops/flight-bot-template` has **Template repository** enabled. The
   connected repository API does not expose that flag for verification here.
2. Existing legacy install `Victoryun0919/flight-bot` still needs its one-time
   v1.5 bootstrap from the owner's authenticated clone.
3. Review the next scheduled daily PTIS run after v1.4/v1.5/v1.6 changes.
4. Optionally run the source **Build Clean PTIS Template** workflow manually once
   to retain a downloadable clean zip artifact; direct workflow dispatch is not
   exposed by the connected tool in this session.

## Version Correction

Before publishing the separate template repository, verification found that
`PTIS_VERSION` was still `1.5.0` after the v1.6 merge. It is corrected to
`1.6.0` before any clean template is published, so installed repositories can
detect v1.6 as a newer upstream version.

## Known Boundary

The connected GitHub tooling can populate the created template repository but does
not expose the GitHub **Template repository** setting itself, so that final flag
requires UI confirmation.

No cross-repository PAT is required for ongoing code updates: the clean template
contains the v1.5 review-only updater, so future PTIS version bumps can arrive as
update branches/PRs without copying upstream runtime/auth files.

## Resume Point

Verify the template-repository checkbox in GitHub Settings. Then perform the
one-time v1.5 bootstrap on `Victoryun0919/flight-bot` from the owner's authenticated
clone and confirm its protected runtime/auth files remain unchanged.
