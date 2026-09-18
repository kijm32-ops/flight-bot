# Checkpoint

## Status

- Current state: V1.5 INSTALLED-USER UPDATE PATH MERGED AND VALIDATED
- Current task: real installed-repository bootstrap/regression validation
- v1.5 merged commit: `8823c32fec7331bb9815a81b3ff054bf2852633a`
- Pull request: `#4` (`PTIS v1.5: add installed-user update path`)
- Validation run: GitHub Actions `35325421779` — success
- SerpAPI usage added by v1.5: 0 calls

## v1.5 Completed

- Added `PTIS_VERSION` as the upstream release/version source of truth.
- Added `.ptis/update_manifest.json` separating centrally managed program files,
  seed-if-missing files, protected files, and future explicit removals.
- Added `update_ptis.py` with:
  - one upstream fetch per check/apply;
  - exact fetched commit pinning;
  - semantic version comparison;
  - manifest/path validation;
  - clean-worktree requirement before apply;
  - managed-file-only updates;
  - one-time `user_config.json` seed when missing;
  - rollback on partial apply failure;
  - read-only `--check` and explicit `--apply`.
- Added `.github/workflows/ptis-update.yml`:
  - weekly + manual checks;
  - deterministic update branch;
  - review-only PR attempt;
  - no automatic merge;
  - pushed-branch fallback when Actions cannot create PRs.
- Existing `data/state.json`, `data/kakao_auth.json`, and
  `user_config.json` are protected from updater writes.
- Repository Secrets remain outside the Git update path and are untouched.
- Added local-Git integration tests and README instructions.

## Validation

GitHub Actions `Validate PTIS` run `35325421779`: passed.

- Python compile: passed
- full unit tests: passed
- workflow YAML parse: passed
- `git diff --check`: passed
- updater integration tests: passed
- no real SerpAPI call was made

## Real Third-party Regression Target

`Victoryun0919/flight-bot` is confirmed to be a legacy install:

- no `focus.py`;
- no `route_watch.py`;
- no `user_config.json`;
- no `.github/workflows/validate.yml`;
- therefore it predates v1.3/v1.4/v1.5.

The connected GitHub integration can read this repository. A collaborator
permission lookup returned 403 from the integration, so write permission remains
unconfirmed.

## Remaining Work

1. Attempt a one-time bootstrap/update branch on `Victoryun0919/flight-bot` only
   if the connected GitHub integration permits writing.
2. If write access is unavailable, give that repository owner the minimal one-time
   bootstrap procedure; after bootstrap, the weekly updater can maintain future
   versions.
3. Review the next scheduled PTIS daily run after v1.4/v1.5 merge.
4. Create a dedicated clean `flight-bot-template` repository when repository
   creation/admin tooling becomes available.

## Known Risks

- Installed repositories may need the GitHub setting that allows Actions to create
  pull requests. Without it, v1.5 leaves a pushed update branch for manual PR
  creation.
- Existing user edits to centrally managed program files are replaced on the
  update branch and must be reviewed before merge.
- Legacy repositories require one bootstrap update before they can self-check.
- The separate clean-template repository is still not created.

## Resume Point

Validate v1.5 against the first real legacy install without touching its protected
runtime/auth state. If write access is unavailable, stop before any remote mutation
and provide the repository owner with the bootstrap commands.
