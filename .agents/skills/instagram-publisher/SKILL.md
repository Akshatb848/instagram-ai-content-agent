---
name: instagram-publisher
description: Implement and review official Instagram Graph API container creation, status polling, idempotent publication, and metrics retrieval for this project.
---

# Instagram publishing

1. Use only the official API; never automate an Instagram login.
2. Require authorised human approval, validated media, empty unsupported claims, and an unused idempotency key.
3. Create a media container, poll with bounded backoff, publish once, and persist every platform identifier and response state.
4. Default to mock mode and `AUTO_PUBLISH=false`. Live tests require an explicit user action and must never run in CI.
5. Redact access tokens and avoid logging query strings that contain credentials.

