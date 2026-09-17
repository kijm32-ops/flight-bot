# Checkpoint

## Status

- Current state: V1.2 FIRST-USER HARDENING MERGED AND VALIDATED
- Current task: next isolated task is PTIS v1.3 Focus Search
- v1.2 source baseline: `fe8ed27307ce8891c07423bc4d4a30a718cf3e23`
- v1.2 merged commit: `37513d5a63c04c300ed2ec3fe49de16948a6541f`
- Pull request: `#1` (`PTIS v1.2: harden first-user setup`)
- Validation run: GitHub Actions `35187032104` — success
- SerpAPI usage added by v1.2: 0 calls

## Real Third-party Validation

The first real guided installation was completed on `Victoryun0919/flight-bot`.
Observed sequence and outcome:

- Git/GitHub CLI were installed but PATH registration required repair.
- Initial installer run was blocked by installer-generated `__pycache__` because
  the template had no `.gitignore`.
- Kakao OAuth browser consent/callback succeeded.
- The first token exchange returned HTTP 401 with insufficient diagnostics.
- After correcting/reissuing the Kakao Client Secret, OAuth and encrypted token
  creation succeeded.
- Git commit then failed with `unable to auto-detect email address` on the new PC.
- After repository-local Git identity configuration, `data/kakao_auth.json` was
  committed and pushed.
- Kakao Setup Verification succeeded and the target user confirmed the message in
  KakaoTalk My Chatroom.
- The copied repository also contained source-instance historical
  `data/state.json`, demonstrating template runtime-state contamination.

## v1.2 Completed

- Added `.gitignore` coverage for Python/cache/local environment artifacts.
- Added GitHub-authenticated repository-local Git identity bootstrap using the
  account's ID-based GitHub `noreply` address.
- Added inherited runtime-state detection/reset for new installations and
  `--preserve-state` for explicit reconfiguration.
- Added rollback for installer-generated state/auth changes before a successful
  setup push, including push-failure handling.
- Moved repository Secret writes until after local Kakao OAuth succeeds.
- Added OAuth retry/change-credentials flow that retains the SerpAPI key in memory.
- Added safe Kakao token endpoint error details without logging secret request data.
- Added `--doctor`, preflight status, setup completion summary, and Pages status check.
- Added `setup_windows.ps1` for the Windows prerequisite/PATH/bootstrap path.
- Added pull-request validation workflow and focused installer/Kakao tests.
- Updated README installation/troubleshooting instructions.

## Validation

- Focused local Python compile: passed.
- Focused local installer/Kakao tests: passed (10 tests).
- GitHub Actions `Validate PTIS` run `35187032104`: passed.
  - dependency installation: passed
  - Python compile: passed
  - full `python -m unittest`: passed
  - all workflow YAML parse: passed
  - `git diff --check`: passed
- PowerShell runtime execution was not available in the Linux validation host;
  `setup_windows.ps1` received static review and should be exercised on the next
  Windows installation.

## Remaining Work

1. Review the first scheduled daily workflow after v1.2 merge for regression.
2. Create a dedicated `kijm32-ops/flight-bot-template` repository and automate a
   clean publication path so runtime files never exist in the distributable source.
   Repository creation is not available through the current connector environment.
3. Start PTIS v1.3 Focus Search as a new isolated task.

## v1.3 Resume Point

Design/implement Focus Search without changing the monthly SerpAPI budget:

- keep the existing Discovery Search behavior;
- add a separate user-intent Focus Search for region/date/stay/max-price conditions;
- use one daily Focus slot by replacing a low-priority discovery slot rather than
  adding a new daily call;
- current candidate replacement: `GMP/near`;
- keep focus results logically separate from normal discovery diversity/exposure
  handling so an explicitly requested destination is not demoted away;
- calculate and verify monthly API usage before implementation;
- do not mix v1.3 changes with installer-hardening code.
