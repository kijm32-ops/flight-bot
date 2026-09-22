# PTIS v1.10 Direct Mobile Trip Settings

## Objective

Make the Pages/Kakao **여행 조건 설정** button open a real settings form directly,
without requiring the user to open GitHub Actions and tap **Run workflow** first.

## Background

PTIS v1.9 linked the button to the manual `workflow_dispatch` page. The form itself
worked, but mobile users still had to navigate GitHub Actions before seeing the
settings fields. Kakao also requires `https://github.com` to be registered under
Product Link Management for this destination.

## Scope

- Add a GitHub Issue Form that contains the existing choice-based trip settings.
- Change the generated settings URL to open that form directly.
- Process owner-authored form submissions with a dedicated GitHub Actions workflow.
- Reuse `manage_trip_settings.py` validation and `user_config.json` persistence.
- Keep the existing `trip-settings.yml` workflow as an administrator fallback.
- Add the new files to updater/template distribution and installer guidance.
- Preserve Discovery, valuation, selection, state, and the one-slot intent scheduler.
- Do not edit `data/state.json` or call SerpAPI.

## Files to Inspect / Change

- `config.py`
- `manage_trip_settings.py`
- `test_manage_trip_settings.py`
- `.github/ISSUE_TEMPLATE/trip-settings.yml`
- `.github/workflows/trip-settings-issue.yml`
- `.github/workflows/validate.yml`
- `.ptis/update_manifest.json`
- `install_ptis.py`
- `README.md`
- `PTIS_VERSION`

## Security / Invariants

- Only the repository owner may apply settings from the public Issue Form.
- Invalid form data must not modify `user_config.json`.
- Manual and Issue Form saves share the `ptis-user-config` concurrency group.
- No secret is placed in the issue body or settings URL.
- Existing manual settings workflow remains available for recovery.

## Usage Estimate

- SerpAPI implementation/test calls: 0.
- Net scheduled SerpAPI calls after deployment: 0.
- One short GitHub Actions run per submitted settings form.

## Validation

- [ ] Python compile passes.
- [ ] Full unit suite passes.
- [ ] Issue-event parsing and owner-only tests pass.
- [ ] Workflow and Issue Form YAML parse.
- [ ] Clean template contains the new form and handler workflow.
- [ ] Pull-request whitespace check passes.
- [ ] No real SerpAPI call is made.

## Completion Criteria

- Pages/Kakao settings buttons point to the direct Issue Form URL.
- The repository owner can submit the form and update `user_config.json`.
- Non-owner submissions cannot change settings.
- Successful settings requests close automatically.
- Existing v1.9 manual settings path continues to work.
