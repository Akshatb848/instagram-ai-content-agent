# External verification runbook

Last verified against official provider documentation: 2026-08-05.

Complete the phases in order. Never paste secrets into Git, issue descriptions, chat, screenshots, workflow JSON, or terminal commands that will be retained in shell history. Store each value directly in the named secret store. Keep `AUTO_PUBLISH=false` throughout setup.

## Phase 1 — Private GitHub repository and Actions secrets

### Acceptance criteria

- The repository is private and the local `main` branch is pushed.
- Actions has read-only repository permissions by default.
- `test.yml` and `security.yml` pass.
- The render workflow can be dispatched with a synthetic UUID but cannot publish.
- Repository/environment secrets exist by name and are never printed.

### Create and protect the repository

1. Sign in to GitHub and select **New repository**.
2. Name it `instagram-ai-content-agent`, select **Private**, and do not add a README, license, or `.gitignore` because the local repository already contains them.
3. In the repository, open **Settings → Actions → General**:
   - Allow actions and reusable workflows required by this repository.
   - Set **Workflow permissions** to **Read repository contents permission**.
   - Do not enable workflows to create or approve pull requests.
4. Open **Settings → Environments → New environment** and create `production`.
5. If the GitHub plan exposes protection rules, add the owner as required reviewer and restrict deployment branches to `main`. Environment secrets are not exposed until protection rules pass.
6. Push from the project directory:

   ```powershell
   git remote add origin https://github.com/OWNER/instagram-ai-content-agent.git
   git push -u origin main
   ```

7. Confirm **Actions** shows `test` and `security` runs. Do not proceed until both pass.

### Add secrets

Navigate to **Settings → Secrets and variables → Actions**. Use repository secrets for test/render integration and the `production` environment for deployment/publishing secrets.

Create only the secrets whose providers have been completed:

| Secret | Location | Source |
| --- | --- | --- |
| `N8N_JOB_ENDPOINT` | Repository | Phase 6 HTTPS URL plus opaque job-fetch path |
| `GITHUB_CALLBACK_SECRET` | Repository | Generate 32 random bytes; same value in n8n secret store |
| `CLOUDINARY_URL` | Repository | Cloudinary dashboard; server-side only |
| `GEMINI_API_KEY` | Repository | Google AI Studio |
| `PEXELS_API_KEY` | Repository | Pexels API account |
| `TELEGRAM_BOT_TOKEN` | Production | BotFather |
| `TELEGRAM_CALLBACK_SECRET` | Production | Generate independently; do not reuse another HMAC key |
| `DATABASE_URL` | Production | Supabase connection panel |
| `INSTAGRAM_ACCESS_TOKEN` | Production | Meta token flow |
| `INSTAGRAM_USER_ID` | Production | Graph API verification response |

Generate independent secrets locally and copy them directly into the secret UI:

```powershell
$bytes = New-Object byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
[Convert]::ToHexString($bytes).ToLowerInvariant()
```

Run the command once per secret. Clear the terminal after securely storing the result.

### Verify and roll back

1. Confirm secret *names* with **Actions secrets** or `gh secret list`; values cannot be read back.
2. Dispatch `render-reel` with a random UUID. Before Phase 4/6 configuration it should fail closed for missing integration configuration, not expose a secret.
3. To roll back, disable Actions, delete affected secrets, revoke the corresponding provider tokens, and remove the remote only if it points to the wrong repository:

   ```powershell
   git remote -v
   git remote remove origin
   ```

Official references: [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments).

## Phase 2 — Google Cloud billing guardrails and eligible VM

### Acceptance criteria

- An active billing account is linked to a dedicated project.
- A monthly project-scoped budget has multiple alert thresholds.
- Exactly one non-preemptible e2-micro is created in an eligible region.
- Boot disk is `pd-standard` and total eligible disk allocation stays at or below 30 GB-months.
- No GPU, TPU, load balancer, paid support, premium image, or other unapproved resource exists.

### Project and billing

1. In Google Cloud Console, create a dedicated project such as `instagram-agent-prod` and record its generated project ID.
2. Link an active billing account. A billing account is required even for the Free Tier.
3. Open **Billing → Budgets & alerts → Create budget**.
4. Scope it to this project and all services. Use a small explicit monthly amount such as the local-currency equivalent of USD 1; this is an alert threshold, not permission to spend.
5. Configure actual-spend alerts at 1%, 50%, 90%, and 100%, plus a forecasted-spend alert. Send alerts to the billing administrators and project owner.
6. Remember: a budget alerts but does not cap charges. The resource restrictions below are the actual guardrail.

### Create the VM

1. Enable the Compute Engine API only.
2. Select one of the currently eligible regions: `us-west1`, `us-central1`, or `us-east1`. Select a zone within it.
3. Create one **non-preemptible** `e2-micro` VM.
4. Use Ubuntu LTS from Google/Canonical, not a paid Marketplace image.
5. Set the boot disk to **Standard persistent disk (`pd-standard`)**, at most 30 GB. Remember the allowance is aggregated as GB-months across the billing account.
6. Add no GPU or TPU. Do not create a load balancer.
7. Use the default network initially. Permit SSH only from a controlled source when possible; expose 80/443 only after Phase 6.
8. Attach a narrowly scoped service account with no editor/owner role. The n8n container does not require broad Google Cloud API access.
9. Add labels such as `application=instagram-agent` and `cost-profile=free-tier`.

Equivalent CLI outline after reviewing all values:

```bash
gcloud config set project PROJECT_ID
gcloud compute instances create instagram-agent-n8n \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --provisioning-model=STANDARD \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-type=pd-standard \
  --boot-disk-size=30GB \
  --no-service-account \
  --no-scopes \
  --labels=application=instagram-agent,cost-profile=free-tier
```

### Verify and roll back

1. Open **Billing → Reports**, filter to this project, and confirm no unexpected SKU.
2. Inspect the VM: machine `e2-micro`, eligible region, standard provisioning, `pd-standard`, disk ≤30 GB, no accelerator.
3. Run `gcloud compute instances describe instagram-agent-n8n --zone=ZONE` and save a redacted configuration record.
4. If any property is wrong, stop and delete the VM before deploying data. Recreate it with eligible settings. Deleting the VM does not necessarily delete separately retained disks; inspect **Compute Engine → Disks** afterward.

Official references: [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features), [budgets and alerts](https://docs.cloud.google.com/billing/docs/how-to/budgets).

## Phase 3 — Gemini API key and free-tier confirmation

### Acceptance criteria

- The AI Studio project reports Free Tier.
- The configured model appears in that project's active rate-limit page and pricing table as free-tier eligible.
- One structured test call succeeds.
- No billing account is linked solely to raise Gemini limits and paid fallback remains disabled.

### Create and store the key

1. Open Google AI Studio and select/create a project dedicated to this application.
2. Open **API keys → Create API key** and select the dedicated project.
3. Copy the key once into `GEMINI_API_KEY` in GitHub Actions and the n8n credential/secret store. Do not put it in `.env` on a shared computer.
4. In the repository/runtime configuration, set `LLM_PROVIDER=gemini` and set `GEMINI_MODEL` to a model that the current pricing and rate-limit pages show as available on Free Tier. Do not assume the example model remains free.
5. Keep `ALLOW_PAID_FALLBACK=false` and `MAX_LLM_RETRIES=2`.

### Verify quota and behavior

1. In AI Studio, open the project's active rate limits. Limits are applied per project, not per key, and vary by model.
2. Record current RPM, TPM, and RPD in the deployment checklist without recording the key.
3. Make one minimal structured-JSON request from the application test command. Confirm valid JSON and usage logging.
4. Temporarily test the quota-error path with the mock provider; verify it records `FREE_TIER_QUOTA_EXHAUSTED` and does not switch providers.
5. Review the Free Tier data-use terms; Free Tier content may be used to improve Google products. Do not send private source material.

### Rotate or roll back

Create a replacement key, update secret stores, verify it, then delete the old key. If accidental paid-tier linkage occurs, stop workflows, remove the key, return to mock mode, and review billing before continuing.

Official references: [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [pricing](https://ai.google.dev/gemini-api/docs/pricing), [billing tiers](https://ai.google.dev/gemini-api/docs/billing).

## Phase 4 — Pexels, Telegram, Cloudinary, and Supabase

Complete each provider independently. Do not combine secrets or reuse passwords/HMAC keys.

### 4A. Pexels

1. Create a Pexels account, review the API terms/documentation, and request the single API key assigned to the account.
2. Store it as `PEXELS_API_KEY` in GitHub/n8n.
3. Send one search request using the `Authorization` header. Do not put the key in the URL.
4. Record `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset` from the successful response.
5. Verify every selected asset retains its Pexels page, creator name/link, license/usage record, and download URL in the render manifest.
6. On failure or suspected exposure, stop media retrieval and request/revoke the key through Pexels support/account controls.

Reference: [Pexels API authorization and quota headers](https://www.pexels.com/api/documentation/).

### 4B. Telegram bot and authorised owner ID

1. In Telegram, open the verified `@BotFather`, send `/newbot`, choose its display name and username, and securely store the returned token as `TELEGRAM_BOT_TOKEN`.
2. Send `/setprivacy` and keep group privacy enabled unless a documented feature requires otherwise. Do not add the bot to groups for this project.
3. Open a private chat with the bot and send `/start`.
4. Before configuring a webhook, call `getUpdates` once from a safe local command and read `message.from.id`; store only that numeric value in `TELEGRAM_AUTHORIZED_USER_IDS`.
5. Generate a separate `TELEGRAM_CALLBACK_SECRET`. The application uses signed, expiring, replay-protected callback payloads in addition to Telegram identity checks.
6. After Phase 6 provides HTTPS, call `setWebhook` with the exact n8n path, an independent `secret_token`, and `allowed_updates=["message","callback_query"]`. Telegram sends that secret in `X-Telegram-Bot-Api-Secret-Token`.
7. Call `getWebhookInfo`; confirm the URL, no last error, and no unexpected pending updates.
8. Send a mock approval request. Confirm an unknown user, expired callback, and replayed callback are rejected.
9. To roll back, call `deleteWebhook` (or `setWebhook` with an empty URL), revoke the token in BotFather, and create a new token before re-enabling.

References: [BotFather tutorial](https://core.telegram.org/bots/tutorial), [Bot API webhook security](https://core.telegram.org/bots/api).

### 4C. Cloudinary temporary media

1. Create a Free account; the current Free plan requires no card and includes a monthly credit allowance. Do not enable paid add-ons.
2. In the product environment **API Keys** page, record the cloud name, API key, and API secret directly into the server-side secret store. Never expose the API secret to browser code.
3. Store the provider URL as `CLOUDINARY_URL` only in GitHub Actions/server secrets.
4. Create a dedicated folder/prefix such as `instagram-agent/temp/` and tag uploads with package ID plus expiry date.
5. Make one signed backend upload of a tiny synthetic video using resource type `video`; record `public_id`, `version`, `secure_url`, bytes, and format.
6. Fetch `secure_url` without authentication and confirm HTTPS because Meta must retrieve it.
7. Delete the test asset using an authenticated destroy call and confirm it no longer resolves after cache expiry.
8. Enforce seven-day deletion and monitor the credit dashboard. On unexpected usage, disable workflows, revoke the API key, delete temporary assets, and inspect logs.

References: [Cloudinary Free plan](https://cloudinary.com/documentation/developer_onboarding_faq_free_plan), [Upload API](https://cloudinary.com/documentation/image_upload_api_reference).

### 4D. Supabase PostgreSQL

1. Create one Free project in the closest suitable region. Generate a unique database password and store it in a password manager.
2. In **Connect**, select the correct connection mode:
   - Prefer the direct connection for migrations/backup when the client has IPv6.
   - Use the shared session pooler on persistent IPv4-only hosts.
   - Do not purchase the IPv4 add-on for this zero-cost profile.
3. Copy the SQLAlchemy-compatible PostgreSQL URL into `DATABASE_URL`. Percent-encode special characters in the password.
4. Create a least-privilege application role/schema rather than using the database owner for routine n8n/application traffic. Keep a separate migration role.
5. Restrict network access where supported and require TLS (`sslmode=require`).
6. Run `alembic upgrade head`, then verify all expected tables and the Alembic version.
7. Insert/read/delete one synthetic workflow record. Run a `pg_dump` and restore it to a disposable local database to prove recoverability.
8. Configure n8n PostgreSQL variables to the same project using its own restricted role; restart n8n and verify `/healthz` plus workflow persistence.
9. To roll back, stop writers, restore the pre-migration backup or downgrade only when the migration explicitly supports it. Rotate the database password if the URL was exposed.

References: [Supabase database overview](https://supabase.com/docs/guides/database/overview), [connection modes](https://supabase.com/docs/guides/database/connecting-to-postgres).

## Phase 5 — Meta app, professional Instagram account, permissions, and token

### Acceptance criteria

- The target account is an Instagram Business or Creator account linked to a Facebook Page.
- The owner has full Page access.
- A dedicated Meta developer app has only required products/permissions.
- The token resolves to the intended Page and Instagram user.
- Container creation/status retrieval works in a test, but media publication is not executed until separately approved.

### Account and Page preparation

1. In Instagram, switch the target account to **Professional** (Business or Creator). Record any account-feature consequences before confirming.
2. Create or select a Facebook Page used only for this brand.
3. Ensure the owner has Facebook access/full control for the Page.
4. In Instagram: **Edit profile → Public business information → Page → Continue**, sign in to Facebook, select the Page, and connect it.
5. In Meta Business settings, confirm the Page and Instagram account belong to the intended portfolio and the owner has the required access.

### Meta app and permissions

1. Sign in to Meta for Developers and create a dedicated app using the business use case offered for Instagram API access.
2. Add the Instagram API/Instagram Graph API and Facebook Login products required by the selected login flow. Do not add unrelated products.
3. Add the exact OAuth redirect URI and data-deletion/privacy URLs. These must use Phase 6 HTTPS.
4. Add the owner as app administrator/developer/tester. Keep the app in Development mode while testing only accounts with roles.
5. For the Facebook Login flow used by this repository, request the minimum set needed for discovery/publishing: `pages_show_list`, `instagram_basic`, `pages_read_engagement`, and `instagram_content_publish`. Add insights/comment permissions only when those features are enabled.
6. Complete business verification and App Review only when publishing for accounts without an app role. Never misrepresent the use case in review materials.

### Token and ID verification

1. Use Meta's official login/OAuth flow or Graph API Explorer to obtain a short-lived user token for the owner with only the required scopes.
2. Exchange it through Meta's official server-side flow for a long-lived user token. Keep the app secret server-side and do not put tokens in URL logs.
3. Query `/me/accounts` with the current Graph API version shown in the app dashboard. Select the intended Page, not the first result.
4. Query the Page's `instagram_business_account{id,username}` field. Confirm the returned username exactly matches the target account; store the ID as `INSTAGRAM_USER_ID`.
5. Inspect the token with Meta's Access Token Debugger. Record app ID, user ID, scopes, expiry, and data-access expiry—never the token value.
6. Store the long-lived token only as `INSTAGRAM_ACCESS_TOKEN` in the production environment/n8n credential store.
7. Use a synthetic public MP4 to create a Reel media container and poll its status. Stop before `media_publish` unless the user separately authorises a test publication at action time.

### Rotation and rollback

If scope/account checks are wrong, revoke the token, remove the app role if appropriate, and repeat the OAuth flow. If a token leaks, immediately invalidate it in Meta settings, rotate the app secret if exposed, remove it from logs/history, and audit publications. Disconnecting the Facebook Page can break API access; document the existing link before changing it.

Official/Meta references: [connect a Page to a professional account](https://www.facebook.com/help/570895513091465), [Meta's official Instagram API collection](https://www.postman.com/meta/instagram/folder/23987686-3a75357f-e106-47ef-a8d9-af1aadf85365).

## Phase 6 — Public HTTPS callback: controlled domain or approved alternative

### Option A (recommended): controlled domain + Caddy

1. Register or select a domain whose DNS you control. Create an `A` record such as `n8n.example.com` pointing to the VM's external IPv4 address and an `AAAA` record only if IPv6 is configured end to end.
2. Restrict the VM firewall to TCP 80/443 publicly and SSH from a controlled source. Do not expose n8n port 5678.
3. Set `DEPLOY_DOMAIN=n8n.example.com` and deploy the repository's Caddy/n8n Compose profile.
4. Confirm Caddy obtains a trusted certificate and `https://n8n.example.com/healthz` returns 200 without a redirect loop.
5. Set n8n's external URL/webhook variables to the HTTPS origin. Use unique, unguessable webhook paths plus HMAC/header authentication.
6. Configure Telegram's webhook with its secret header. Configure GitHub callbacks to the signed callback endpoint. Add Meta webhook verification only if metrics/comment subscriptions require it.
7. Test from a network outside the VM. Confirm HTTP redirects to HTTPS, TLS is valid, direct `:5678` is unreachable, unsigned requests are rejected, and a valid signed request succeeds once.

### Option B (zero-cost, no custom domain): Tailscale Funnel

Tailscale Funnel is currently beta but available on all plans and supplies a stable TLS-enabled `*.ts.net` name. Use it only after explicitly accepting that external dependency and beta status.

1. Create a Tailscale Personal tailnet and install Tailscale on the VM.
2. Authenticate the VM with a reusable or ephemeral auth method stored outside Git. Enable MagicDNS and HTTPS.
3. Restrict Funnel permission in the tailnet policy to the single VM/operator rather than every member.
4. Keep n8n bound to loopback/internal Docker networking and run:

   ```bash
   sudo tailscale funnel --bg 5678
   tailscale funnel status
   ```

5. Record the stable `https://HOST.TAILNET.ts.net` URL as `PUBLIC_BASE_URL`. Reconfigure n8n webhook URLs and provider callbacks.
6. Perform the same external, unsigned, replay, and health tests as Option A. Funnel accepts public internet traffic; application authentication remains mandatory.
7. To roll back, run `sudo tailscale funnel reset`, revoke the VM from the tailnet, and remove provider webhook URLs.

### Final callback verification

1. Telegram `getWebhookInfo`: correct HTTPS URL, no error, expected pending-update count.
2. GitHub render callback: invalid HMAC rejected; valid HMAC accepted once; replay rejected.
3. Meta verification challenge (only if configured): correct verify token succeeds; wrong token fails.
4. Logs: correlation IDs present, secrets/tokens/signatures absent.
5. Keep `AUTO_PUBLISH=false` after all callback tests.

References: [Telegram webhook requirements](https://core.telegram.org/bots/api), [Tailscale Funnel](https://tailscale.com/kb/1223/funnel), [Tailscale free Personal plan](https://tailscale.com/kb/1154/free-plans-discounts).

## Final go/no-go record

Do not mark external verification complete until every applicable item is checked:

- [ ] GitHub private repository, protected environment, secrets, and passing Actions.
- [ ] Google project/billing/budget plus eligible VM/disk inspection.
- [ ] Gemini project/model visibly on Free Tier and structured test passed.
- [ ] Pexels quota/attribution test passed.
- [ ] Telegram authorised-user, webhook-secret, expiry, and replay tests passed.
- [ ] Cloudinary upload/public-fetch/delete lifecycle passed.
- [ ] Supabase migration, restricted role, application transaction, backup, and restore passed.
- [ ] Meta Page/account/scopes/token IDs verified; no unapproved publication performed.
- [ ] HTTPS external tests passed and direct n8n port is closed.
- [ ] All secret values absent from Git and logs.
- [ ] `AUTO_PUBLISH=false` and `ALLOW_PAID_FALLBACK=false` confirmed in the deployed runtime.

