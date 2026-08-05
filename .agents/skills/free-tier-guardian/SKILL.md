---
name: free-tier-guardian
description: Enforce this project's zero-cost quotas, no-paid-fallback policy, infrastructure limits, retention, and fail-closed behavior before external calls or rendering.
---

# Free-tier guardrails

1. Enforce weekly, per-run, retry, duration, concurrency, and retention limits in application code before dispatch.
2. Never select a paid provider or upgrade automatically; require `ALLOW_PAID_FALLBACK=false`.
3. On exhaustion, persist `FREE_TIER_QUOTA_EXHAUSTED`, notify once, and stop retries.
4. Keep the default VM to one eligible e2-micro with no GPU, load balancer, or oversized disk.
5. Mark eligibility and current provider quotas as user-verified deployment prerequisites because they can change.

