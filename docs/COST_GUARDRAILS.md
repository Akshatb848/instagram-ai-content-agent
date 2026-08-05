# Cost guardrails

The application enforces three Reels per week, 30 source items per run, two LLM retries, two render attempts, one concurrent render, 60 seconds per video, seven-day cloud media retention, three-day Actions artifact retention, no automatic publishing, and no paid fallback.

Google Cloud is excluded because its free tier is exhausted. The active profile uses an already-owned machine plus Tailscale Funnel, with no cloud-compute resource to upgrade accidentally. Provider plans and quotas still change: re-check GitHub Actions minutes, Gemini model eligibility, Supabase limits, Cloudinary credits, and Tailscale Personal/Funnel terms before deployment.
