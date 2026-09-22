# Checkpoint

## Status

- Current state: PTIS v1.10 direct mobile trip settings merged to `main`.
- Merge commit: `3e15ece` (PR #12)
- PTIS_VERSION: `1.10.0`
- SerpAPI usage added: 0 calls; scheduled budget remains unchanged.

## Completed

- Added `.github/ISSUE_TEMPLATE/trip-settings.yml` as the direct mobile settings form.
- Changed Pages/Kakao **여행 조건 설정** to open the Issue Form directly.
- Added `.github/workflows/trip-settings-issue.yml` to validate and apply owner-authored requests.
- Reused `manage_trip_settings.py` for the existing exact-route, region-focus, pause,
  date-generation, and input-validation logic.
- Added an owner check in both workflow gating and issue-event parsing.
- Kept `.github/workflows/trip-settings.yml` as the administrator fallback.
- Shared the existing `ptis-user-config` concurrency group across both save paths.
- Added the form/workflow to `.ptis/update_manifest.json` and clean-template validation.
- Updated installer/README guidance to register both the Pages domain and
  `https://github.com` in Kakao Product Link Management.
- Bumped PTIS to 1.10.0.
- Did not modify `data/state.json`.

## Changed Files

- New: `.github/ISSUE_TEMPLATE/trip-settings.yml`
- New: `.github/workflows/trip-settings-issue.yml`
- Updated: `config.py`, `manage_trip_settings.py`, `test_manage_trip_settings.py`
- Updated: `.github/workflows/validate.yml`, `.ptis/update_manifest.json`
- Updated: `install_ptis.py`, `README.md`, `PTIS_VERSION`, `TASK.md`, `CHECKPOINT.md`

## Validation Performed

- PR #12 final Validate PTIS run #14: passed.
- Python compile: passed.
- Full unit suite: passed, 86 tests.
- GitHub workflow YAML and Issue Form YAML parse: passed.
- Clean-template build: passed, 43 files.
- New Issue Form and handler workflow presence in clean template: passed.
- `git diff --check`: passed.
- No real SerpAPI call was made.

## Remaining Work

1. Open **여행 조건 설정** from Kakao or the next regenerated Pages report and
   confirm the dedicated settings form appears directly.
2. Submit a real settings change only after choosing the desired trip values;
   this changes `user_config.json`.
3. Update downstream template/install repositories separately if immediate v1.10
   distribution is required.

## Current Blockers / Known Issues

- GitHub Issue Forms require GitHub sign-in to submit.
- The final submit button is GitHub's **Submit new issue** UI; it cannot be renamed
  to a PTIS-specific button without adding a separate authenticated backend.
- `AGENTS.md` and `PROJECT_GUIDE.md` are not present in the repository main
  branch; the project-provided copies were used for the work procedure.

## Resume Point

Perform a non-destructive mobile smoke test by opening the direct settings form.
Do not submit a configuration change until the desired trip values are chosen.

## Risks

- Public visitors can open issues in a public repository, but the settings workflow
  does not run unless the issue author is the repository owner and the PTIS title
  prefix is present.
- If Issues are disabled in a downstream installation, the direct settings form
  will not be available; the existing manual Actions workflow remains the fallback.

## Next Action

Open the new direct settings form from Kakao without submitting it.
