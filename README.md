# PTIS Personal Template

PTIS finds discounted Google Flights fares with SerpAPI, publishes a GitHub Pages
report, and can send the summary to your own KakaoTalk "My Chatroom". This is a
personal template: each installation uses its own GitHub repository, SerpAPI key,
and Kakao Developers app.

## What stays private

`data/kakao_auth.json` contains an encrypted Kakao refresh token and is committed
to your repository so GitHub Actions can retain refresh-token rotations. It cannot
be decrypted without the `KAKAO_TOKEN_ENCRYPTION_KEY` GitHub secret. Do not commit
that secret, your Kakao client secret, or a plaintext refresh token. Restrict write
access to the repository because writers can alter a workflow that reads secrets.

## Recommended: guided setup in about 10 minutes

Use this path when installing PTIS for one person. It registers the required
GitHub Actions secrets, opens Kakao OAuth, commits only the encrypted refresh
token, and can run the real My Chatroom verification in one guided session.

Prerequisites:

- Python 3.11 or newer
- Git
- [GitHub CLI](https://cli.github.com/) signed in with `gh auth login`
- A clean local clone made from this template

First create your repository with **Use this template**, clone it, and run:

```bash
python -m pip install -r requirements.txt
python install_ptis.py
```

The assistant shows the exact Kakao Redirect URI and Pages domain for your
GitHub account. After you finish the Kakao Developers settings, it asks for the
SerpAPI key, Kakao REST API key, and Kakao Login Client Secret using hidden
prompts. Secret values are kept in process memory, passed to `gh secret set`
through standard input, and are never written to a plaintext config file or
included in command-line arguments.

You personally approve Kakao access once in the browser. The assistant then:

1. creates a fresh token-encryption key and saves all required repository secrets;
2. obtains and encrypts the Kakao Refresh Token;
3. commits and pushes only `data/kakao_auth.json`;
4. opens the GitHub Pages setting;
5. optionally runs **Kakao Setup Verification** and waits for its result.

If the template copy initially contains an unreadable `data/kakao_auth.json`, that
is expected: it was encrypted for a different installation. The assistant replaces
it using a new encryption key unique to your repository.

GitHub and Kakao intentionally require their own login/consent steps, so those
buttons cannot be bypassed safely. Everything between those required approvals is
handled by the assistant.

## Manual setup fallback

Use the steps below if GitHub CLI is unavailable or if you prefer to configure
each item yourself.

1. Click **Use this template** on GitHub and create your own repository. Keep the
   default branch as `main`. Enable GitHub Pages with **GitHub Actions** as its
   source in **Settings > Pages**.
2. Create a SerpAPI account and copy its API key.
3. In [Kakao Developers](https://developers.kakao.com/), create an app, enable
   **Kakao Login**, and register this exact Redirect URI under Kakao Login:
   `http://127.0.0.1:8765/callback`.
4. Under **Product Link Management**, register your Pages web domain:
   `https://YOUR_GITHUB_OWNER.github.io`. In **Consent Items**, enable
   **KakaoTalk Message (`talk_message`)**. Copy the REST API key and Client Secret.
   Client Secret is normally enabled by default for new REST API keys.
5. In your repository's **Settings > Secrets and variables > Actions**, add:

   | Secret | Required | Value |
   | --- | --- | --- |
   | `SERPAPI_KEY` | Yes | Your SerpAPI key |
   | `KAKAO_REST_API_KEY` | For Kakao | Kakao REST API key |
   | `KAKAO_CLIENT_SECRET` | Recommended | Kakao Client Secret; required when it is enabled in Kakao Developers |
   | `KAKAO_TOKEN_ENCRYPTION_KEY` | For Kakao | A new key generated in step 6 |
   | `KAKAO_JS_KEY` | Optional | Kakao JavaScript key for the report's share button |
   | `GMAIL_USER` / `GMAIL_PASSWORD` | Optional | Gmail address and app password for email notifications |

6. Clone your new repository locally, install dependencies, and generate a fresh
   encryption key. Store that printed value as `KAKAO_TOKEN_ENCRYPTION_KEY` before
   continuing.

   ```bash
   python -m pip install -r requirements.txt
   python setup_kakao.py --print-encryption-key
   ```

7. Set the following local environment variables, then run the OAuth setup. The
   browser opens a Kakao consent page. Sign in and grant **KakaoTalk Message**.
   The script verifies that `talk_message` was granted and creates only the
   encrypted `data/kakao_auth.json` file.

   ```bash
   KAKAO_REST_API_KEY=your-rest-key
   KAKAO_CLIENT_SECRET=your-client-secret
   KAKAO_TOKEN_ENCRYPTION_KEY=the-key-from-step-6
   KAKAO_REDIRECT_URI=http://127.0.0.1:8765/callback
   python setup_kakao.py
   ```

   In PowerShell, set each value with `$env:NAME = 'value'` before the command.
   Never put the values into a committed `.env` file.

8. Commit and push the encrypted token file, then run **Kakao Setup Verification**
   from the repository's **Actions** tab. A successful run sends one test message
   to your KakaoTalk My Chatroom. This is the required proof path before relying on
   the daily workflow.

   ```bash
   git add data/kakao_auth.json
   git commit -m "Configure Kakao OAuth"
   git push
   ```

9. Run **Daily Flight Deal Scraper** manually once. It publishes the Pages report
   and thereafter runs at 07:00 KST. Gmail remains optional; leave its two secrets
   empty to use Kakao and Pages only.

## Token rotation

The daily workflow reads and decrypts `data/kakao_auth.json`, refreshes the access
token, and immediately writes a newly returned refresh token back to that encrypted
file before sending a message. The workflow commits this file together with its
normal state update. Kakao currently returns a replacement refresh token only when
the prior token has under one month remaining, so an absent replacement is normal.

## URLs and template behavior

On GitHub Actions, the report URL is calculated as
`https://OWNER.github.io/REPOSITORY/` from `GITHUB_REPOSITORY`, and the Kakao card
image URL is calculated from the same repository plus the running commit SHA. No
account name is embedded in the application code. For a custom domain or a local
notification test, set `PTIS_PAGE_URL` and `PTIS_KAKAO_CARD_IMAGE_URL` explicitly.

The current default message endpoint is `POST /v2/api/talk/memo/default/send`;
it sends only to the user who completed OAuth.
PTIS does not request the separate permission required for sending to friends.

## Troubleshooting

- `talk_message` missing: confirm the consent item is enabled, run OAuth setup
  again, and grant consent in the browser.
- `KOE` token error: confirm the REST API key, Client Secret setting, and matching
  `KAKAO_TOKEN_ENCRYPTION_KEY`; repeat OAuth setup if the token was revoked.
- Callback timeout: the registered URI and local `KAKAO_REDIRECT_URI` must exactly
  match `http://127.0.0.1:8765/callback`, and port 8765 must be available.
- No Kakao card image: make the repository public, or set
  `PTIS_KAKAO_CARD_IMAGE_URL` to a publicly reachable image. Kakao fetches card
  images itself.

## Development validation

```bash
python -m unittest
python -m py_compile *.py
```
