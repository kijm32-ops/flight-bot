# PTIS v1.6 Clean Template Distribution

## Objective

Prepare a reproducible clean distribution artifact for new PTIS installations so
the operator's runtime state/auth files are never copied into a new user's
repository.

## Background

The upstream source repository is also a live PTIS installation. It contains
runtime files such as `data/state.json` and `data/kakao_auth.json`. The guided
installer can reset inherited state, but the cleaner design is to distribute only
program files plus safe seed configuration.

Repository creation for a separate `kijm32-ops/flight-bot-template` repository is
not available through the connected GitHub tooling in this session, so this task
must stop at a reproducible clean template artifact and publish workflow. The
actual repository-creation/admin step remains separate.

## Scope

- Add a deterministic template builder that uses the existing
  `.ptis/update_manifest.json` as the primary allowlist.
- Include centrally managed program files.
- Include seed-if-missing files such as the disabled default
  `user_config.json`.
- Explicitly exclude protected runtime/auth files.
- Do not include `TASK.md`, `CHECKPOINT.md`, or other upstream development
  operating documents unless they are part of the managed-file manifest.
- Do not include `.git`, caches, local virtualenvs, generated reports, or
  runtime output.
- Validate every manifest-referenced source file before building.
- Fail closed if a protected file overlaps with managed output.
- Produce a clean directory and zip artifact suitable for initializing a separate
  GitHub template repository.
- Add a GitHub Actions workflow that builds and uploads the clean template
  artifact without making any SerpAPI calls.
- Add tests proving runtime/auth exclusion and deterministic contents.

## Distribution Rules

The clean template must not contain:

- `data/state.json`
- `data/kakao_auth.json`
- any repository Secret
- live runtime history
- generated Pages output

The clean template may contain:

- all manifest `managed_files`;
- all manifest `seed_if_missing` files;
- no other files by default.

## Explicit Non-goals

- Do not create the separate GitHub repository if repository-creation tooling is
  unavailable.
- Do not add a cross-repository push token or PAT in this task.
- Do not change flight search, valuation, selection, carryover, Focus, Route Watch,
  updater, or API budget behavior.
- Do not edit `data/state.json`.

## Validation

- `python -m py_compile *.py`
- `python -m unittest`
- workflow YAML parse
- `git diff --check`
- clean template build test
- protected files absent
- all managed files present
- seed files present
- development-only docs absent
- deterministic repeated build file list
- no real SerpAPI call

## Completion Criteria

- A clean template directory/zip can be built from upstream `main` reproducibly.
- Protected runtime/auth files cannot enter the artifact.
- CI validates the artifact.
- The only remaining step is repository administration: create
  `flight-bot-template` and publish the verified artifact there.
