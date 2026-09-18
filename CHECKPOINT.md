# Checkpoint

## Status

- Current state: V1.5 INSTALLED-USER UPDATE PATH IMPLEMENTED ON FEATURE BRANCH; VALIDATION PENDING
- Current task: PTIS v1.5 Installed-user Update Path
- Feature branch: `ptis-v1.5-update-path`
- Base: latest `main` after v1.4 Exact Route Watch
- SerpAPI usage added by v1.5: 0 calls

## v1.5 Implemented

- Added `PTIS_VERSION` as the upstream release/version source of truth.
- Added `.ptis/update_manifest.json` separating:
  - centrally managed program files;
  - seed-if-missing user files;
  - protected user/runtime files;
  - future explicit removals.
- Added `update_ptis.py`:
  - one upstream fetch per check/apply;
  - exact fetched commit pinned for the entire update;
  - semantic version comparison;
  - manifest validation and safe relative-path checks;
  - clean-worktree requirement before apply;
  - managed-file checkout only;
  - `user_config.json` seed only when missing;
  - protected runtime/auth/config files never overwritten;
  - rollback to HEAD if an apply operation fails part-way;
  - read-only `--check` and explicit `--apply` modes.
- Added `.github/workflows/ptis-update.yml`:
  - weekly check plus manual dispatch;
  - installed repositories only (upstream source repo skips the job);
  - creates a deterministic update branch;
  - attempts to open a review-only PR;
  - never auto-merges;
  - leaves a pushed update branch and warning if Actions PR creation is disabled.
- Added integration tests using temporary local Git repositories.
- Added README instructions and legacy one-time bootstrap note.

## Protected State

The update mechanism must preserve existing content in:

- `data/state.json`
- `data/kakao_auth.json`
- `user_config.json`

GitHub Secrets remain outside the Git update path and are untouched.

A missing legacy `user_config.json` may be seeded once with the upstream default.

## Validation

Pending pull-request CI:

- Python compile
- full unit tests
- workflow YAML parse
- `git diff --check`
- updater integration tests
- no real SerpAPI call

## Remaining Work

1. Open v1.5 PR and inspect **Validate PTIS**.
2. Fix only updater-related failures if CI is not green.
3. Merge v1.5 after validation.
4. Attempt the one-time bootstrap/update on `Victoryun0919/flight-bot` as the
   first real installed-repository regression case, only if write permission is
   available through the connected GitHub account.
5. If write permission is unavailable, provide the exact one-time bootstrap path
   for that repository owner.
6. Create a dedicated clean `flight-bot-template` repository separately when
   repository creation/admin tooling is available.

## Known Risks

- GitHub Actions PR creation depends on the installed repository allowing Actions
  to create pull requests. The workflow degrades to a pushed update branch when
  that permission is unavailable.
- Existing user edits to centrally managed program files are intentionally
  replaced by upstream on an update, but only inside a reviewable branch/PR.
- Legacy repositories need one bootstrap update before they can self-check weekly.
- `TASK.md` and `CHECKPOINT.md` are intentionally not centrally managed in
  installed repositories; they are upstream development-operating documents.

## Resume Point

Run v1.5 PR validation. If green, merge, then test the bootstrap against the first
real third-party repository without modifying protected user state.
