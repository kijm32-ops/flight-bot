# PTIS Personal Template

PTIS finds discounted Google Flights fares with SerpAPI, publishes a GitHub Pages
report, and can send the summary to your own KakaoTalk "My Chatroom". Each personal
installation uses its own GitHub repository, SerpAPI key, and Kakao Developers app.

## What stays private

`data/kakao_auth.json` contains only an encrypted Kakao refresh token. GitHub Actions
can decrypt it only with the repository's `KAKAO_TOKEN_ENCRYPTION_KEY` secret. Never
commit that encryption key, the Kakao Client Secret, a plaintext refresh token, or
other API keys. Restrict repository write access because a writer can change a
workflow that reads repository secrets.

## Recommended guided setup

### Windows

After creating your repository with **Use this template** and cloning it, open
PowerShell in the repository folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1
```

The bootstrap checks Python 3.11+, Git, and GitHub CLI. It repairs the current
PowerShell PATH for the standard Git and GitHub CLI install locations when those
programs are already installed. If a prerequisite is actually missing, it prints
the official `winget` command instead of silently installing software. It also runs
`gh auth login` when needed, installs `requirements.txt`, and starts the guided
installer.

### macOS / Linux / already-prepared Windows

Prerequisites:

- Python 3.11 or newer
- Git
- [GitHub CLI](https://cli.github.com/) authenticated with `gh auth login`
- a clean local clone created from the PTIS template

Run:

```bash
python -m pip install -r requirements.txt
python install_ptis.py
```

For read-only diagnostics at any time:

```bash
python install_ptis.py --doctor
```

The doctor checks Python/Git/GitHub CLI readiness, GitHub authentication, the
repository remote, working-tree state, Git commit identity presence, required
repository Secret names, encrypted Kakao auth file presence, Pages status, and the
latest Kakao verification status. It does not print secret values.

## What the guided installer does

Before asking for secrets, the installer performs a preflight check and configures
missing **repository-local** Git author settings from the authenticated GitHub
account. It uses GitHub's ID-based `noreply` commit address, so a fresh PC does not
need manual `git config user.email` setup.

A GitHub template snapshot can contain runtime history from the source instance.
For a new personal installation the installer detects meaningful history in
`data/state.json` and asks to reset it before proceeding. This gives the new user
an independent 30-day price history, exposure log, carryover state, and monthly API
budget. When deliberately reconfiguring an existing installation, run:

```bash
python install_ptis.py --preserve-state
```

After preflight, configure the Kakao Developers app with the values printed by the
installer. The fixed local Redirect URI is:

```text
http://127.0.0.1:8765/callback
```

The installer then asks through hidden prompts for:

- SerpAPI key
- Kakao REST API key
- Kakao Login Client Secret

It creates the token-encryption key itself. Secret values remain in process memory
and are never placed in command-line arguments or a plaintext config file.

The setup order is transactional:

1. perform local Kakao OAuth and verify `talk_message`;
2. if OAuth fails, retry with the same Kakao values or replace only the Kakao values
   without re-entering the SerpAPI key;
3. after OAuth succeeds, save the four required GitHub Actions secrets;
4. commit and push the new installation state and encrypted refresh token;
5. check/open GitHub Pages settings when Pages is not yet enabled;
6. optionally run **Kakao Setup Verification** and wait for the real My Chatroom
   delivery result;
7. print a final status summary containing only verified/observed states.

If setup stops before the setup commit is successfully pushed, installer-generated
changes to the state/auth files are rolled back so a retry starts from a clean
repository.

## Kakao Developers settings

Create a Kakao Developers app for the person who will receive messages, then:

1. Enable **Kakao Login**.
2. Register `http://127.0.0.1:8765/callback` as the Redirect URI.
3. Enable the `talk_message` consent item.
4. Enable the Kakao Login Client Secret for the REST API key.
5. Under Product Link Management, register the Pages web domain printed by the
   installer, normally `https://YOUR_GITHUB_OWNER.github.io`.

The OAuth browser consent must be completed while signed into the Kakao account
that should receive PTIS messages.

## Manual setup fallback

Use this only when GitHub CLI is unavailable or you prefer to configure everything
manually.

1. Enable GitHub Pages with **GitHub Actions** as its source in repository Settings.
2. Create a SerpAPI account and obtain its API key.
3. Configure the Kakao Developers app as described above.
4. Add these repository Actions secrets:

   | Secret | Required | Value |
   | --- | --- | --- |
   | `SERPAPI_KEY` | Yes | Your SerpAPI key |
   | `KAKAO_REST_API_KEY` | For Kakao | Kakao REST API key |
   | `KAKAO_CLIENT_SECRET` | For Kakao | Client Secret paired with that REST API key |
   | `KAKAO_TOKEN_ENCRYPTION_KEY` | For Kakao | Fresh Fernet key generated below |
   | `KAKAO_JS_KEY` | Optional | Kakao JavaScript key for report sharing |
   | `GMAIL_USER` / `GMAIL_PASSWORD` | Optional | Gmail address and app password |

5. Generate the encryption key:

   ```bash
   python setup_kakao.py --print-encryption-key
   ```

6. Set `KAKAO_REST_API_KEY`, `KAKAO_CLIENT_SECRET`,
   `KAKAO_TOKEN_ENCRYPTION_KEY`, and
   `KAKAO_REDIRECT_URI=http://127.0.0.1:8765/callback` in the local shell, then run:

   ```bash
   python setup_kakao.py
   ```

7. Commit only the encrypted `data/kakao_auth.json`, then run **Kakao Setup
   Verification** in Actions.

## Token rotation

The daily workflow reads and decrypts `data/kakao_auth.json`, refreshes the Kakao
access token, and persists a newly returned refresh token atomically before message
delivery. The workflow commits that encrypted file together with normal runtime
state updates when it changes.

## URLs and template behavior

On GitHub Actions, the report URL is calculated as
`https://OWNER.github.io/REPOSITORY/` from `GITHUB_REPOSITORY`. The Kakao card image
URL is also derived from the running repository and revision. `PTIS_PAGE_URL` and
`PTIS_KAKAO_CARD_IMAGE_URL` remain explicit overrides for a custom domain or local
test.

The Kakao delivery endpoint sends only to the OAuth user's own My Chatroom. PTIS
does not request the separate friend-message permission.

A dedicated clean distribution repository is still planned so runtime files never
appear in the source template snapshot. Until that repository exists, the guided
installer's runtime-state reset is required for new personal installations.

## Troubleshooting

- **Installer says the repository is dirty immediately after start:** update to the
  current template containing `.gitignore`, remove only generated cache directories
  if present, then run `python install_ptis.py --doctor`.
- **Kakao token HTTP 401:** the current setup script prints Kakao's safe
  `error`/`error_description`/`error_code` fields when available. Verify the REST
  API key and the Client Secret from the same REST key entry, and confirm the
  Client Secret is enabled.
- **Callback timeout:** the registered Redirect URI must exactly match
  `http://127.0.0.1:8765/callback`, and local port 8765 must be available.
- **Git commit identity:** guided setup configures this automatically only inside
  the current repository. `--doctor` reports whether an identity is available.
- **No Kakao card image:** the image URL must be publicly reachable by Kakao.
- **Setup interrupted before commit:** rerun the installer. It rolls back the local
  runtime/auth changes it generated before a successful setup commit.

## Focus Search

Focus Search adds one explicit user-intent search without increasing the normal
monthly SerpAPI budget. When enabled, it replaces the lowest-priority daily
`GMP/near` discovery task one-for-one. When disabled or expired, the original
`GMP/near` task runs normally.

Edit `user_config.json`:

```json
{
  "focus_search": {
    "enabled": true,
    "origin": "ICN",
    "region": "Japan",
    "outbound_from": "2026-10-02",
    "outbound_to": "2026-10-11",
    "stay_min": 3,
    "stay_max": 5,
    "max_price": 250000
  }
}
```

Required when enabled: `origin`, `region`, `outbound_from`, and
`outbound_to`. `stay_min` and `stay_max` are optional but must be supplied
together. `max_price` is optional.

The current Google Flights Deals API does not allow `query` and `trip_length`
in the same request. PTIS therefore expresses a requested stay such as 3-5 days
inside the region query while keeping the explicit outbound-date window. Focus
results still pass PTIS normalization and price-safety gates, but they do not
compete with discovery quota, carryover, or exposure demotion. They appear first
in Kakao and in a separate Pages section.

If the entire focus date window has passed, Focus Search is skipped automatically
and the normal `GMP/near` discovery slot is restored. Invalid Focus settings also
disable only Focus for that run; the discovery pipeline continues.

## Schedule and API budget

The normal workflow still runs every day at UTC 22:00 (KST 07:00). Focus Search
uses a replacement slot rather than an additional call, so the normal schedule
remains about **221 calls/month** (7 daily tasks plus the weekly deep task) against
the 235-call safety budget. v1.3 adds **0 net scheduled SerpAPI calls**.

## Development validation

```bash
python -m py_compile *.py
python -m unittest
```

Pull requests also run **Validate PTIS**, which compiles Python, runs unit tests,
parses workflow YAML, and checks diff whitespace without calling SerpAPI.
