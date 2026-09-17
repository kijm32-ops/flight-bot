# PTIS Personal Template v1.2 First-user Hardening

## Objective

Harden the guided PTIS installer using failures observed during the first real
third-party installation, without changing flight collection, valuation,
selection, carryover, or daily SerpAPI usage.

## Background

The first end-to-end install on `Victoryun0919/flight-bot` reached real Kakao
My Chatroom delivery, but exposed setup-path defects that local mocked tests did
not catch:

- importing the installer could create `__pycache__` in a repository with no
  `.gitignore`, causing the installer's own clean-worktree guard to fail;
- Kakao token exchange failures surfaced only as generic HTTP 401 errors;
- OAuth succeeded but the encrypted-token commit failed when Git author identity
  was not configured on the new PC;
- a GitHub template copy inherited the source operator's `data/state.json` and
  encrypted `data/kakao_auth.json`;
- an OAuth failure forced the user to restart setup and re-enter unrelated
  values;
- Windows had Git and GitHub CLI installed but their install directories were not
  on the current PowerShell `PATH`.

## Scope

- Add repository-local Git identity bootstrap from the authenticated GitHub user,
  using GitHub's ID-based `noreply` address.
- Add `.gitignore` entries for Python caches, virtual environments, and local
  environment files.
- Make a new personal installation reset inherited PTIS runtime history before
  committing its own encrypted Kakao token. Existing installations can opt into
  `--preserve-state`.
- Roll back installer-generated runtime/auth file changes when setup stops before
  a successful commit/push.
- Keep SerpAPI and Kakao values in memory across retryable OAuth/secret-write
  failures; permit replacing only the Kakao values after an OAuth failure.
- Surface safe Kakao token endpoint diagnostics (`error`, `error_description`,
  `error_code`) without logging authorization codes, API keys, tokens, or secrets.
- Add `--doctor` read-only diagnostics, a clear preflight checklist, and a final
  verified-status summary.
- Add a minimal Windows PowerShell bootstrap that repairs known Git/GitHub CLI
  PATH locations, checks Python 3.11+, guides missing prerequisite installation,
  authenticates `gh`, installs dependencies, and starts the installer.
- Add a non-SerpAPI validation workflow for compile/tests/YAML/diff checks.
- Update installation documentation and checkpoint state.

## Explicit Non-goals

- Do not change `config.py` search profiles, SerpAPI task scheduling, normalization,
  valuation, selection, exposure, carryover, notification content, or report layout.
- Do not modify the source repository's current `data/state.json` contents.
- Do not add a SerpAPI smoke call to setup; setup must add 0 monthly SerpAPI calls.
- Do not implement Focus Search in this task. That is the next task after v1.2.

## Template Distribution Constraint

A dedicated clean distribution repository remains the preferred architecture so
runtime files never appear in a template snapshot. The available GitHub connector
cannot create a new repository, and `kijm32-ops/flight-bot-template` does not yet
exist. v1.2 therefore fixes correctness immediately by resetting inherited runtime
state transactionally during guided setup. Creating/publishing the dedicated
clean template repository remains a separate repository-administration step.

## Usage Estimate

- SerpAPI: 0 additional calls.
- Kakao: unchanged; one local OAuth authorization and one optional setup verification.
- GitHub: repository Secret writes, one setup commit/push, optional verification run.

## Validation

- `python -m py_compile *.py`
- `python -m unittest`
- YAML parse for every workflow
- `git diff --check` on the pull request diff
- focused tests for Git identity, inherited-state reset/preserve, OAuth retry, safe
  Kakao diagnostics, and secret-via-stdin behavior
- PowerShell bootstrap syntax/static review; execute it only on a Windows host
  where PowerShell is available

## Completion Criteria

- A clean/new clone cannot fail only because Python created `__pycache__`.
- Missing Git author identity cannot block the encrypted-token commit.
- A guided new installation starts with independent runtime state.
- A Kakao 401 exposes a safe actionable KOE/error description when Kakao returns it.
- OAuth retry does not require re-entering the SerpAPI key.
- `--doctor` reveals setup readiness without printing secret values.
- Full Python tests and workflow validation pass without making SerpAPI calls.
