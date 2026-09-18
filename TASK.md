# PTIS v1.5 Installed-user Update Path

## Objective

Let repositories that were already installed from PTIS detect and receive newer
PTIS program versions without overwriting personal runtime/auth/config state.

## Background

The first real third-party installation, `Victoryun0919/flight-bot`, is now
behind the upstream PTIS source. It predates v1.3 Region Focus and v1.4 Exact
Route Watch. Template copies are independent repositories, so upstream feature
commits do not propagate automatically.

## Scope

- Add `PTIS_VERSION` as the upstream version source of truth.
- Add a manifest that explicitly separates:
  - centrally managed program files;
  - seed-if-missing personal config files;
  - protected installation-specific files.
- Add `update_ptis.py` that:
  - fetches one upstream snapshot;
  - compares local/upstream PTIS versions;
  - applies only manifest-managed files from that exact snapshot;
  - seeds `user_config.json` only when missing;
  - never writes protected runtime/auth/config files;
  - supports read-only check mode and explicit apply mode;
  - refuses a dirty worktree by default.
- Add a GitHub Actions update-check workflow for installed repositories.
- The workflow should open/update a user-reviewable update branch/PR rather than
  silently updating the default branch.
- Provide a local/manual fallback.
- Add regression tests proving runtime/auth/user config preservation.
- Use `Victoryun0919/flight-bot` as the first real compatibility target after
  upstream validation.

## Protected Installation State

The updater must never overwrite these existing user files:

- `data/state.json`
- `data/kakao_auth.json`
- `user_config.json`

GitHub repository Secrets are outside the Git tree and must remain untouched.

If `user_config.json` does not exist in a legacy install, the current upstream
default may be seeded once. After that, it is user-owned.

## Update Model

Upstream source:

- repository: `kijm32-ops/flight-bot`
- branch: `main`
- version file: `PTIS_VERSION`

Installed repository update:

1. fetch upstream `main` once;
2. read the version and update manifest from the fetched commit;
3. if newer, copy only managed files from that exact commit;
4. seed missing user config only;
5. review/test changes on an update branch;
6. merge the PR only after user approval.

The updater must not depend on a dedicated clean template repository. That
repository remains desirable for new installs but is a separate admin task.

## GitHub Actions Behavior

- Weekly scheduled check plus manual `workflow_dispatch`.
- No SerpAPI calls.
- On an update:
  - create/reset a deterministic update branch for the target version;
  - commit only updater-generated changes;
  - push the branch;
  - open a PR if one is not already open.
- If GitHub repository settings do not permit Actions to create PRs, the pushed
  update branch should remain reviewable and the workflow should explain the
  manual PR fallback.

## Explicit Non-goals

- Do not silently merge updates.
- Do not update GitHub Secrets.
- Do not modify `data/state.json`, `data/kakao_auth.json`, or an existing
  `user_config.json`.
- Do not create `kijm32-ops/flight-bot-template` in this task if repository
  creation tooling is unavailable.
- Do not change flight search, valuation, selection, carryover, or API budget.

## Validation

- `python -m py_compile *.py`
- `python -m unittest`
- workflow YAML parse
- `git diff --check`
- updater integration test using temporary local Git repositories
- legacy install with no `PTIS_VERSION`
- managed-file replacement
- seed-if-missing user config
- preserve existing user config
- preserve `data/state.json`
- preserve `data/kakao_auth.json`
- dirty-worktree refusal
- same-version no-op
- no real SerpAPI call

## Completion Criteria

- An old independent PTIS repository can be brought to the current code through a
  reviewable update.
- Existing runtime/auth/user config content is byte-for-byte preserved.
- Subsequent upstream versions can use the same mechanism without adding bespoke
  migration code for ordinary managed-file updates.
- Full validation passes before merge.
