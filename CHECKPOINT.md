# Checkpoint

## Status

- Current state: V1.6 CLEAN TEMPLATE ARTIFACT IMPLEMENTED; VALIDATION PENDING
- Current task: PTIS v1.6 Clean Template Distribution
- Feature branch: `ptis-v1.6-clean-template`
- Base: latest `main` after v1.5 installed-user updater
- SerpAPI usage added by v1.6: 0 calls

## v1.6 Implemented

- Added `build_template.py` using `.ptis/update_manifest.json` as the allowlist.
- Clean output contains only managed files plus seed-if-missing files.
- Protected runtime/auth files are rejected from the artifact.
- Added deterministic zip generation.
- Added `test_build_template.py` covering:
  - all manifest files present;
  - `data/state.json` absent;
  - `data/kakao_auth.json` absent;
  - safe disabled `user_config.json` present;
  - development-only TASK/CHECKPOINT absent;
  - repeated zip builds byte-identical;
  - output-inside-source refusal.
- Added **Build Clean PTIS Template** workflow to build, verify, and upload the zip.
- README now describes the clean-distribution path.

## Validation

Pending pull-request CI:

- Python compile
- full unit tests
- workflow YAML parse
- `git diff --check`
- no real SerpAPI call

## Remaining Work

1. Open v1.6 PR and run **Validate PTIS**.
2. Merge after green CI.
3. Run **Build Clean PTIS Template** on main and verify its artifact.
4. Repository-admin boundary: create `kijm32-ops/flight-bot-template`, populate it
   from the verified artifact, and mark that repository as a GitHub template.
5. Existing legacy install `Victoryun0919/flight-bot` still needs its one-time
   v1.5 bootstrap from the owner's authenticated clone.

## Known Boundary

The connected GitHub tooling in this session does not expose repository creation.
No cross-repository PAT or automatic push was added. This is intentional: the
source build/publish artifact is implemented and verified separately from the
one-time repository-admin action.

## Resume Point

Validate and merge v1.6. Then run the clean-template build workflow on main. The
only unresolved new-install distribution step should be creating and initializing
the separate template repository.
