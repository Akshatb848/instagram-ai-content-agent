# Manual Actions Required

No manual action is required for local mocked implementation.

External verification requires the owner to:

1. Create/select a private GitHub repository and approve repository secrets.
2. Keep an owned Windows/Linux machine online and approve Tailscale Funnel for its public HTTPS endpoint. Google Cloud is no longer used.
3. Create a Gemini API key and confirm the selected model's free-tier quota.
4. Create Pexels, Telegram, Cloudinary, and Supabase credentials.
5. Configure a Meta app, Instagram professional account, required permissions, and a long-lived access token.
6. Use the Tailscale-provided `*.ts.net` HTTPS name, or supply a domain only if selecting the Cloudflare Tunnel fallback.

Do not paste personal passwords. Use platform secret stores for tokens and keys.

Follow the complete sequence in `docs/EXTERNAL_SETUP.md`.

Complete these actions using the ordered procedures and acceptance checks in `docs/EXTERNAL_VERIFICATION_RUNBOOK.md`.
