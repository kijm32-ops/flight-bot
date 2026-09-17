# Checkpoint

## Status

- Current state: V1.2 HARDENING IMPLEMENTED ON FEATURE BRANCH, VALIDATION IN PROGRESS
- Current task: PTIS Personal Template v1.2 First-user Hardening
- Source baseline: `fe8ed27307ce8891c07423bc4d4a30a718cf3e23`
- Feature branch: `ptis-v1.2-first-user-hardening`
- SerpAPI usage added by this task: 0 calls

## Real Third-party Validation Completed Before v1.2

The first real guided installation was completed on `Victoryun0919/flight-bot`.
Observed sequence and outcome:

- Git/GitHub CLI installation was present but PATH registration required repair.
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
- The copied repository was also confirmed to contain source-instance historical
  `data/state.json`, demonstrating template runtime-state contamination.

## v1.2 Changes

- Added Python/local environment ignores to prevent installer-created cache files
  from tripping the clean-worktree guard.
- Added GitHub-authenticated repository-local Git identity bootstrap using an
  ID-based GitHub `noreply` commit address.
- Added inherited runtime-state detection/reset for new installations and
  `--preserve-state` for explicit reconfiguration.
- Added pre-commit rollback for state/auth files and push-failure commit rollback.
- Moved repository Secret writes until after local Kakao OAuth succeeds.
- Added OAuth retry/change-credentials flow that keeps the SerpAPI key in memory.
- Added safe Kakao token endpoint error details without logging secret request data.
- Added `--doctor`, preflight status, setup completion summary, and Pages status check.
- Added `setup_windows.ps1` for the Windows prerequisite/PATH/bootstrap path.
- Added pull-request validation workflow and focused installer/Kakao tests.
- Updated README installation/troubleshooting instructions.

## Validation

- Focused local compile for v1.2 Python files: passed.
- Focused local unit tests for installer and Kakao diagnostics: passed (10 tests).
- Full repository test suite / workflow YAML / PR diff validation: pending GitHub
  pull-request validation run.
- PowerShell execution validation: not available in the current Linux container;
  script receives static review and must be exercised on the next Windows install.

## Remaining Work

1. Run/inspect the v1.2 pull-request validation workflow and merge only if green.
2. Review the next scheduled daily workflow after merge for regression.
3. Create a dedicated `kijm32-ops/flight-bot-template` repository and automate a
   clean publication path so runtime files never exist in the distributable source.
   Repository creation is blocked in the current connector environment.
4. Start the next isolated task: PTIS v1.3 Focus Search (region/date intent search,
   one daily focus slot replacing a discovery slot so monthly API usage stays flat).

## Resume Point

- Inspect the v1.2 PR validation result. If green, merge v1.2, then begin a new
  `TASK.md` for Focus Search. Do not mix Focus Search into the installer-hardening
  branch.
