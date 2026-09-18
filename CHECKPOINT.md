# Checkpoint

## Status

- Current state: V1.6 CLEAN TEMPLATE DISTRIBUTION MERGED AND VALIDATED
- Current task: template repository administration / artifact publication
- v1.6 merged commit: `dba1d068efc526b8eb99d42332bb4b011949d347`
- Pull request: `#5` (`PTIS v1.6: add clean template distribution artifact`)
- Validation run: GitHub Actions `35342347236` — success
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

## Remaining Work

1. Confirm the post-merge **Build Clean PTIS Template** workflow run and inspect the
   uploaded artifact.
2. Repository-admin boundary: create `kijm32-ops/flight-bot-template`, populate it
   from the verified artifact, and mark it as a GitHub template repository.
3. Existing legacy install `Victoryun0919/flight-bot` still needs its one-time
   v1.5 bootstrap from the owner's authenticated clone.
4. Review the next scheduled daily PTIS run after v1.4/v1.5/v1.6 changes.

## Known Boundary

The connected GitHub tooling in this session does not expose repository creation.
No cross-repository PAT or automatic push was added. The source build artifact is
implemented and validated separately from the one-time repository-admin action.

At the time this checkpoint was written, no post-merge workflow run was yet visible
for commit `dba1d068efc526b8eb99d42332bb4b011949d347`; artifact publication therefore
still needs confirmation.

## Resume Point

Confirm the clean-template artifact workflow. Then create and initialize the
separate template repository using the verified artifact. After that, new-user
installation distribution and existing-user update delivery are separate, clean
paths.
