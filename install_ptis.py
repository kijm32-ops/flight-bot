"""Guided one-command installer for a personal PTIS repository."""

import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import webbrowser

from kakao_auth import AUTH_FILE, generate_encryption_key


ROOT = Path(__file__).resolve().parent
REDIRECT_URI = "http://127.0.0.1:8765/callback"
SETUP_WORKFLOW = "kakao-setup-test.yml"
SECRET_NAMES = (
    "SERPAPI_KEY",
    "KAKAO_REST_API_KEY",
    "KAKAO_CLIENT_SECRET",
    "KAKAO_TOKEN_ENCRYPTION_KEY",
)


class InstallError(RuntimeError):
    """Raised when the guided installer cannot continue safely."""


def _run(args, *, input_text=None, env=None, capture=False, check=True):
    return subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        input=input_text,
        text=True,
        capture_output=capture,
        check=check,
    )


def _parse_repository_slug(remote_url: str) -> str:
    value = remote_url.strip()
    patterns = (
        r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return match.group(1)
    raise InstallError("The origin remote is not a supported GitHub repository URL.")


def _repository_slug() -> str:
    result = _run(
        ["git", "config", "--get", "remote.origin.url"],
        capture=True,
    )
    return _parse_repository_slug(result.stdout)


def _require_command(name: str) -> None:
    if not shutil.which(name):
        raise InstallError(f"Required command is missing: {name}")


def _require_clean_worktree() -> None:
    result = _run(["git", "status", "--porcelain"], capture=True)
    if result.stdout.strip():
        raise InstallError(
            "The repository has uncommitted changes. Commit or stash them before setup."
        )


def _prompt_secret(label: str) -> str:
    value = getpass.getpass(f"{label}: ").strip()
    if not value:
        raise InstallError(f"{label} cannot be empty.")
    return value


def _set_repository_secret(repository: str, name: str, value: str) -> None:
    _run(
        ["gh", "secret", "set", name, "--repo", repository],
        input_text=value,
    )


def _run_kakao_oauth(rest_key: str, client_secret: str, encryption_key: str) -> None:
    env = os.environ.copy()
    env.update(
        {
            "KAKAO_REST_API_KEY": rest_key,
            "KAKAO_CLIENT_SECRET": client_secret,
            "KAKAO_TOKEN_ENCRYPTION_KEY": encryption_key,
            "KAKAO_REDIRECT_URI": REDIRECT_URI,
        }
    )
    _run([sys.executable, "setup_kakao.py"], env=env)
    if not AUTH_FILE.exists():
        raise InstallError("Kakao OAuth completed without creating the encrypted auth file.")


def _commit_encrypted_token() -> None:
    _run(["git", "add", str(AUTH_FILE.relative_to(ROOT))])
    changed = _run(["git", "diff", "--cached", "--quiet"], check=False)
    if changed.returncode == 0:
        raise InstallError("The encrypted Kakao auth file did not change.")
    _run(["git", "commit", "-m", "Configure Kakao OAuth"])
    _run(["git", "push"])


def _latest_workflow_run(repository: str):
    result = _run(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repository,
            "--workflow",
            SETUP_WORKFLOW,
            "--event",
            "workflow_dispatch",
            "--limit",
            "1",
            "--json",
            "databaseId,status,conclusion,url",
        ],
        capture=True,
    )
    rows = json.loads(result.stdout)
    return rows[0] if rows else None


def _run_delivery_test(repository: str) -> None:
    before = _latest_workflow_run(repository)
    before_id = before.get("databaseId") if before else None
    _run(
        [
            "gh",
            "workflow",
            "run",
            SETUP_WORKFLOW,
            "--repo",
            repository,
            "--ref",
            "main",
        ]
    )
    run = None
    for _ in range(20):
        time.sleep(2)
        candidate = _latest_workflow_run(repository)
        if candidate and candidate.get("databaseId") != before_id:
            run = candidate
            break
    if not run:
        raise InstallError("The Kakao verification workflow did not appear in time.")
    print(f"Verification run: {run['url']}")
    _run(
        [
            "gh",
            "run",
            "watch",
            str(run["databaseId"]),
            "--repo",
            repository,
            "--exit-status",
        ]
    )


def main() -> int:
    print("PTIS Personal guided setup")
    print("Secrets stay in memory and are sent directly to GitHub Actions secrets.")
    try:
        _require_command("git")
        _require_command("gh")
        _require_clean_worktree()
        _run(["gh", "auth", "status"])
        repository = _repository_slug()
        owner = repository.split("/", 1)[0]
        pages_domain = f"https://{owner}.github.io"

        print("\nBefore continuing, configure your Kakao Developers app:")
        print(f"- Redirect URI: {REDIRECT_URI}")
        print(f"- Product Link web domain: {pages_domain}")
        print("- Kakao Login: ON")
        print("- Consent item talk_message: optional or required consent")
        print("- Kakao Login Client Secret: ON")
        webbrowser.open("https://developers.kakao.com/console/app")
        input("Press Enter after the Kakao app settings are complete...")

        serpapi_key = _prompt_secret("SerpAPI key")
        rest_key = _prompt_secret("Kakao REST API key")
        client_secret = _prompt_secret("Kakao Login Client Secret")
        encryption_key = generate_encryption_key()

        values = {
            "SERPAPI_KEY": serpapi_key,
            "KAKAO_REST_API_KEY": rest_key,
            "KAKAO_CLIENT_SECRET": client_secret,
            "KAKAO_TOKEN_ENCRYPTION_KEY": encryption_key,
        }
        print("\nSaving encrypted repository secrets...")
        for name in SECRET_NAMES:
            _set_repository_secret(repository, name, values[name])

        print("\nOpening Kakao consent. Approve KakaoTalk Message access once.")
        _run_kakao_oauth(rest_key, client_secret, encryption_key)
        print("Saving the encrypted refresh token to the repository...")
        _commit_encrypted_token()

        pages_settings = f"https://github.com/{repository}/settings/pages"
        print(f"\nEnable GitHub Actions as the Pages source if needed: {pages_settings}")
        webbrowser.open(pages_settings)

        answer = input("Send one Kakao My Chatroom verification message now? [Y/n] ").strip()
        if answer.lower() not in {"", "y", "yes"}:
            print("Setup is saved. Run Kakao Setup Verification from Actions later.")
            return 0
        _run_delivery_test(repository)
        print("\nPTIS setup succeeded. Check KakaoTalk My Chatroom for the test message.")
        return 0
    except (InstallError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"PTIS setup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
