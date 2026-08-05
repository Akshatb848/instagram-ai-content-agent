# Cost guardrails

The application enforces three Reels per week, 30 source items per run, two LLM retries, two render attempts, one concurrent render, 60 seconds per video, seven-day cloud media retention, three-day Actions artifact retention, no automatic publishing, and no paid fallback.

Before VM creation, manually verify current Google Cloud Always Free eligibility for the chosen e2-micro region and standard disk. Create a small budget alert; an alert does not cap spend, so also avoid GPUs, load balancers, premium network tiers, static IPv4 unless confirmed eligible, and oversized disks. Provider plans and quotas change; re-check them before each deployment.

