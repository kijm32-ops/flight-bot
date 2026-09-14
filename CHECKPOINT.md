# Checkpoint

## Status

- Current state: KAKAO DELIVERY VERIFIED
- Current task: PTIS Personal Template v1
- Source baseline: `69988414061cc4c778a7840e53929338e1e05bff`
- Deployment: pushed to `main` as `5411298` on 2026-09-14.
- Repository settings: Template Repository enabled; GitHub Pages is live from
  GitHub Actions at `https://kijm32-ops.github.io/flight-bot/`.
- Kakao app: Login Client Secret enabled, `talk_message` consent configured, and
  the Pages web domain / local OAuth callback are registered.

## Completed

- Read operating documents, cloned and verified source commit
  `69988414061cc4c778a7840e53929338e1e05bff`, and recorded the task harness.
- Replaced account-specific deployment URLs with repository-derived configuration.
- Added encrypted refresh-token storage, Client Secret support, and atomic rotation.
- Added local OAuth setup with `talk_message` scope verification and a manual Actions
  workflow that sends a real Kakao "My Chatroom" setup-test message.
- Documented template installation; Gmail remains optional.
- Stored the real Kakao Refresh Token only as encrypted `data/kakao_auth.json`.
  The encryption key and Kakao Login Client Secret are GitHub Actions secrets.
- Ran **Kakao Setup Verification** on `main` successfully (GitHub Actions run
  `34840765911`, 14 seconds). The `send-test-message` job succeeded.

## Changed Files

- `config.py`, `notifier.py`, `main.py`, `requirements.txt`
- `kakao_auth.py`, `setup_kakao.py`, `test_kakao_auth.py`
- `.github/workflows/schedule.yml`, `.github/workflows/kakao-setup-test.yml`
- `README.md`, `test_carryover.py`, `TASK.md`, `CHECKPOINT.md`
- Removed `.github/workflows/kakao-smoke-test.yml` (superseded by encrypted-setup verification).

## Validation Performed

- `python -m py_compile` for every Python file: passed.
- `python -m unittest`: passed, 22 tests.
- Mocked encrypted store, wrong-key rejection, Client Secret request, rotation
  persistence, and successful message result-code paths: passed.
- YAML parsed for every workflow: passed.
- Repository-derived Pages/card URL assertion: passed.
- `git diff --check`: passed.

## Remaining Work

1. Review the first scheduled daily workflow after it runs.
2. Optionally remove the legacy `KAKAO_REFRESH_TOKEN` repository secret only
   after the next scheduled delivery succeeds.

## Resume Point

- Review the next **Daily Flight Deal Scraper** workflow. Do not change
  collection, valuation, selection, normalization, or `data/state.json` without
  a new task.
