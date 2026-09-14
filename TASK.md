# PTIS Personal Template v1

## Objective

Enable a person to install PTIS from their own GitHub repository, SerpAPI account,
and Kakao Developers app, then run unattended Kakao "send to me" notifications.

## Session Scope

- Replace account-specific Pages and Kakao card URLs with repository-derived values.
- Add Kakao client-secret support and encrypted refresh-token persistence/rotation.
- Add local OAuth setup, a GitHub Actions smoke-test path, installation instructions,
  and focused tests.
- Preserve the SerpAPI collection, normalization, valuation, selection, and state
  behavior. Do not edit `data/state.json`.

## Usage Estimate

- SerpAPI: 0 additional calls. Existing seven daily tasks and Saturday deep task are
  unchanged.
- Kakao: one local OAuth authorization and one optional smoke-test message during
  installation; regular execution still refreshes one access token only when there
  are deals to send.

## Assumptions Verified

- Current source commit is `69988414061cc4c778a7840e53929338e1e05bff`.
- `notifier.py` currently reads a plaintext refresh-token secret directly and has
  no client secret or rotation store.
- `schedule.yml` currently commits only `data/state.json`.
- Kakao's current documentation requires `talk_message`, supports `client_secret`,
  and may return a replacement refresh token when fewer than 30 days remain.

## Validation

- Python compile and unit tests, including mocked refresh/rotation paths.
- YAML parse for every workflow.
- Import smoke checks for the existing main path.
- `git diff --check`.

## Completion Criteria

- No account-specific URL remains in executable configuration or workflows.
- A rotated token is encrypted and atomically persisted before message delivery.
- A user can obtain `talk_message` consent through the documented local OAuth path
  and then run an authenticated GitHub Actions smoke test.
