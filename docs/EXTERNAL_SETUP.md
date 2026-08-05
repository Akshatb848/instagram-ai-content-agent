# External setup: zero-cost production profile

This guide replaces Google Compute Engine with an always-on machine you already control plus Tailscale Funnel. The machine runs Docker, n8n, and PostgreSQL; Tailscale supplies a public HTTPS `*.ts.net` address. GitHub Actions performs video rendering. This has no mandatory cloud-compute bill, but it is only available while the machine and internet connection are online.

Do not paste credentials into issues, chat, Git, screenshots, or workflow JSON. Put local secrets in `.env` and GitHub-only secrets in repository or protected environment secrets.

## Phase A — Private GitHub repository

### Acceptance criteria

- The repository is private, the local `main` branch has been pushed, Actions can read code only, and no secret is present in Git history.

### Steps

1. Sign in to GitHub and select **New repository**.
2. Name it `instagram-ai-content-agent`, choose **Private**, and do not add a README, license, or `.gitignore because these already exist locally.
3. On the new repository page, copy its HTTPS or SSH URL.
4. In the project directory, run:

   ```powershell
   git remote add origin https://github.com/YOUR_ACCOUNT/instagram-ai-content-agent.git
   git remote -v
   git push -u origin main
   ```

5. Open **Settings → Actions → General**:
   - Allow only actions used by this repository or verified actions.
   - Set workflow permissions to **Read repository contents**.
   - Do not enable pull requests from forks to receive secrets.
6. Open **Settings → Environments → New environment**, create `production`, enable required reviewers, and add yourself as reviewer. Store publication secrets here so a render cannot publish without approval.
7. Open **Settings → Secrets and variables → Actions**. Create repository secrets:

   | Secret | Purpose |
   | --- | --- |
   | `N8N_JOB_ENDPOINT` | Signed HTTPS endpoint used to fetch an opaque render job |
   | `GITHUB_CALLBACK_SECRET` | Random 32-byte HMAC key shared with n8n |
   | `CLOUDINARY_URL` | Cloudinary server-side credential URL |

   Add `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID` only to the protected `production` environment, not repository-wide.
8. Generate HMAC keys locally without displaying them in logs:

   ```powershell
   $bytes = New-Object byte[] 32
   [Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
   [Convert]::ToHexString($bytes).ToLower()
   ```

9. Run **Actions → test → Run workflow**. Confirm test, lint, typing, migration, and workflow validation pass.
10. Review **Billing and plans → Plans and usage** monthly. Private repositories receive plan-dependent included Actions minutes; usage beyond the allowance can be charged, so do not configure a payment method for Actions and retain the repository's concurrency/time limits.

### Rollback

Delete the remote repository only after preserving a local clone. Remove a bad secret under **Actions secrets**, rotate it at the provider, and review workflow logs.

## Phase B — Zero-cost host and public HTTPS

### Architecture

```text
Internet callbacks -> Tailscale Funnel HTTPS -> 127.0.0.1:5678 n8n
                                             -> local PostgreSQL
n8n -> GitHub Actions renderer -> Cloudinary -> Instagram API
```

### Acceptance criteria

- Docker starts at boot, the machine does not sleep, n8n is bound only to loopback, Funnel returns n8n's health response over HTTPS, and no router port is forwarded.

### Steps

1. Choose a machine you own that can remain online. Windows 11 with Docker Desktop/WSL2 is supported for this repository. Use a UPS if outages are common.
2. Disable automatic sleep while plugged in. Keep automatic screen locking enabled.
3. Enable Docker Desktop **Start Docker Desktop when you sign in** and WSL2 integration. Do not expose Docker's daemon over TCP.
4. Install Tailscale from its official download page, sign in, and keep **MagicDNS** enabled.
5. In the Tailscale admin console, rename the machine to `instagram-agent`, enable HTTPS certificates, and approve Funnel when prompted.
6. Start the local stack:

   ```powershell
   docker compose -f docker-compose.local.yml up -d --build postgres n8n
   Invoke-WebRequest http://127.0.0.1:5678/healthz -UseBasicParsing
   ```

7. Expose only n8n through Funnel:

   ```powershell
   tailscale funnel --bg 5678
   tailscale funnel status
   ```

8. Copy the displayed URL, normally `https://instagram-agent.YOUR-TAILNET.ts.net`. This becomes `PUBLIC_BASE_URL`, `WEBHOOK_URL`, and `N8N_EDITOR_BASE_URL`.
9. Create `.env` from `.env.example` and set:

   ```text
   PUBLIC_BASE_URL=https://instagram-agent.YOUR-TAILNET.ts.net
   WEBHOOK_URL=https://instagram-agent.YOUR-TAILNET.ts.net/
   N8N_EDITOR_BASE_URL=https://instagram-agent.YOUR-TAILNET.ts.net/
   N8N_SECURE_COOKIE=true
   ```

10. Recreate n8n, then verify externally from a phone with Wi-Fi disabled:

    ```powershell
    docker compose -f docker-compose.local.yml up -d n8n
    Invoke-WebRequest https://instagram-agent.YOUR-TAILNET.ts.net/healthz -UseBasicParsing
    ```

11. In Tailscale access controls, restrict which tailnet members may administer the Funnel node. Funnel itself is public; application webhooks must still validate HMAC/Telegram secrets.
12. Configure Windows Update active hours and schedule controlled monthly reboots. After every reboot verify Docker, containers, Funnel, and `/healthz`.

### Limitations and fallback

- Funnel is subject to non-configurable bandwidth limits and supports only the tailnet's `*.ts.net` name.
- A power, ISP, Windows, Docker, or Tailscale outage makes callbacks unavailable.
- If Funnel is unsuitable, Cloudflare Tunnel is the supported alternative, but stable production hostnames normally require a domain you control. Do not use a temporary quick-tunnel URL for Meta or Telegram production callbacks.

### Rollback

Run `tailscale funnel 5678 off`, confirm the public URL no longer responds, and keep n8n locally accessible at `127.0.0.1:5678`.

## Phase C — Gemini free-tier API

### Acceptance criteria

- A Google AI Studio API key works with a currently free-tier model, billing is not enabled for the project, and the application stops rather than switching to paid use.

### Steps

1. Sign in to Google AI Studio and open **Get API key**.
2. Create a separate project named `instagram-agent-free`; do not link a billing account.
3. Create an API key and restrict it to the Generative Language API where the console permits.
4. On the official pricing and rate-limit pages, choose a model explicitly listed in the Free Tier. Set `GEMINI_MODEL` to that exact model ID; never rely on a moving `latest` alias.
5. Store the key only as local `GEMINI_API_KEY`. Set:

   ```text
   LLM_PROVIDER=gemini
   ALLOW_PAID_FALLBACK=false
   MAX_LLM_RETRIES=2
   ```

6. Make one minimal structured-JSON test request, record the model ID and returned usage, then revoke any test key exposed in terminal history.
7. In AI Studio, review usage after the test. Confirm the project remains on Free Tier and no billing account is attached.
8. Configure quota handling to record `FREE_TIER_QUOTA_EXHAUSTED`, notify Telegram once, and stop until the quota window resets.

### Privacy note

The Gemini free tier may use submitted content to improve Google's products. Send only public-source content; do not submit credentials, private drafts, personal data, or unpublished business information.

### Rollback

Set `LLM_PROVIDER=mock`, revoke the key in AI Studio, and restart n8n.

## Phase D — Pexels, Telegram, Cloudinary, and Supabase

### D1. Pexels

1. Create a Pexels account and request an API key from the Pexels API page.
2. Read and accept the current API and license terms. Preserve photographer, Pexels URL, asset ID, and license context with every selected asset.
3. Store the key as `PEXELS_API_KEY` locally.
4. Test one curated-video search. Cache results, honor response rate-limit headers, and never hot-loop searches.
5. Reject assets without a stable origin or those unsuitable for the Reel's intended use. Do not remove attribution records even when visible attribution is not mandatory.

### D2. Telegram approval bot

1. In Telegram, open the verified `@BotFather`, run `/newbot`, choose a name and unique username, and copy the token into a password manager.
2. Send the new bot `/start` from the only account allowed to approve publication.
3. Temporarily call `getUpdates`, find `message.from.id`, and store that numeric ID as `TELEGRAM_AUTHORIZED_USER_IDS`. Never use a display name for authorization.
4. Generate a separate 32-byte `TELEGRAM_CALLBACK_SECRET`.
5. Configure the webhook to the Funnel URL and include Telegram's `secret_token`. The receiver must validate both `X-Telegram-Bot-Api-Secret-Token` and the repository's signed, expiring, one-time callback payload.
6. Test Approve, Reject, Regenerate, Sources, and Cancel with a mock package. Confirm another Telegram account is rejected and a callback cannot be replayed.
7. Use `/revoke` in BotFather immediately if the token is exposed.

### D3. Cloudinary temporary media

1. Create a Free Programmable Media account; no credit card is required.
2. In **Settings → API Keys**, create a dedicated key for this application. Store cloud name, API key, and API secret; never use unsigned uploads for final Reels.
3. Set `CLOUDINARY_URL` only in GitHub Actions and the orchestrator secret store.
4. Upload one small synthetic MP4 as `resource_type=video` with a unique package ID, `overwrite=false`, and a seven-day expiry tag/metadata.
5. Verify the returned `secure_url` is publicly fetchable by Meta, then destroy the test asset using a signed server-side request.
6. Keep `CLOUD_MEDIA_RETENTION_DAYS=7`; delete after publication or expiry. Review the 25-credit monthly dashboard weekly.

### D4. Supabase PostgreSQL

1. Create a Supabase Free project in the closest suitable region and generate a strong database password.
2. In **Connect**, copy the pooled SQLAlchemy/PostgreSQL connection string. Use the transaction pooler for short-lived automation connections when recommended by the project dashboard.
3. Store the connection as `DATABASE_URL`; URL-encode special characters in the password.
4. In **Database → Roles**, create a least-privilege application role for the project schema. Do not use the dashboard owner/service role from n8n workflows.
5. Restrict network access if the plan/project supports it. Require TLS (`sslmode=require`).
6. Run `alembic upgrade head`, seed sources, and perform an insert/read/delete smoke test.
7. Export an encrypted logical backup because the Free plan does not include automatic backups. Test restoration locally every month.
8. Supabase may pause a Free project after one week of inactivity. The scheduled source workflow should create legitimate weekly database activity; monitor for pause notifications rather than artificial high-frequency pings.

### Phase D verification

- Pexels returns a licensed test asset with attribution metadata.
- Telegram rejects an unknown user, expired signature, invalid signature, and replay.
- Cloudinary uploads and deletes a synthetic MP4.
- Supabase migration and CRUD smoke tests pass over TLS.

## Phase E — Meta app and Instagram publishing

### Preconditions

- Use an Instagram Professional account (Business or Creator). Do not provide the Instagram or Facebook password to the application.
- Complete all testing with Meta test users/assets. Keep `AUTO_PUBLISH=false`.

### Steps

1. Convert the target Instagram account to Professional in Instagram settings if necessary.
2. In Meta for Developers, create a separate app for this project and select the business/content-publishing use case offered by the current dashboard.
3. Add the Instagram product. Prefer the current **Instagram API with Instagram Login** flow when available; follow the dashboard's exact permission names. For the older Facebook Login flow, link the Instagram professional account to a Facebook Page first.
4. Add the Tailscale Funnel HTTPS URL to allowed domains, redirect URIs, deauthorization callback, and data-deletion callback fields where required.
5. Add only the required permissions for profile discovery, content publishing, and permitted insights. Do not request messaging, ads, or unrelated Page permissions.
6. Add yourself as app administrator/tester and accept the invitation in the relevant Meta/Instagram account.
7. Generate a short-lived test token using Meta's official login/token tool, exchange it for the supported long-lived token, and record its expiry. Store it as the protected `production` environment secret `INSTAGRAM_ACCESS_TOKEN`.
8. Obtain and store the official Instagram user ID as `INSTAGRAM_USER_ID`. Confirm it belongs to the intended professional account before any container creation.
9. In development mode, test:
   - create a Reel media container using the Cloudinary `secure_url`;
   - poll container status with bounded backoff;
   - stop before the publish call and verify the stored identifiers;
   - after an explicit human approval, perform exactly one test publication;
   - read the returned media ID/permalink and save them.
10. Implement token-expiry alerts at 14 days and 3 days. Rotate using Meta's supported flow before expiry.
11. Complete App Review and business verification only if Meta requires them for publishing outside app-role accounts. Supply a screencast of the approval-first flow and clear data-use/deletion instructions.
12. After verification, keep app roles minimal, enable app-secret proof where supported, and review security alerts monthly.

### Rollback

Set `AUTO_PUBLISH=false`, deactivate WF-07, revoke the token in Meta, remove the app integration from Instagram, and preserve publication/audit records.

## Phase F — Final integration and go-live gate

1. Confirm the local host, Docker, PostgreSQL/Supabase, and Funnel survive a reboot.
2. Verify the public health endpoint and every signed callback from an external network.
3. Run the full mock pipeline, then the sandbox pipeline with real Pexels/Gemini/Telegram/Cloudinary credentials and no Meta publish call.
4. Render a 30-second synthetic Reel. Confirm 1080×1920, H.264, AAC, subtitles, safe margins, cover, manifest, attribution, and checksum.
5. Confirm the weekly/free-tier guards stop a fourth Reel, a third retry, a second concurrent render, and paid fallback.
6. Confirm the repository and n8n exports contain no credentials.
7. Take and restore an encrypted database/n8n backup.
8. Authorize one test publication explicitly. Record Meta's media ID and permalink; do not infer success from the request alone.
9. Keep all workflows inactive except the tested schedule/failure/approval routes. Activate publishing last.
10. Review usage dashboards weekly and stop any provider before its free allowance is exceeded.

## Official references

- GitHub Actions secrets: https://docs.github.com/en/actions/concepts/security/secrets
- GitHub Actions billing and usage: https://docs.github.com/en/actions/concepts/billing-and-usage
- Tailscale Funnel: https://tailscale.com/kb/1223/funnel
- Tailscale free plans: https://tailscale.com/docs/reference/free-plans-discounts
- Gemini pricing: https://ai.google.dev/gemini-api/docs/pricing
- Telegram bots and webhooks: https://core.telegram.org/bots and https://core.telegram.org/bots/webhooks
- Cloudinary plans and uploads: https://cloudinary.com/documentation/billing_and_plans and https://cloudinary.com/documentation/image_upload_api_reference
- Supabase pricing: https://supabase.com/pricing
- Instagram Platform: https://developers.facebook.com/docs/instagram-platform/

