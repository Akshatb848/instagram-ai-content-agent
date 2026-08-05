---
name: n8n-workflow-author
description: Create, edit, and validate this repository's exported n8n workflow JSON, including secret-free nodes, signed webhooks, error routes, idempotency, and import verification.
---

# n8n workflow authoring

1. Keep exports in `n8n/workflows` and credentials referenced by names or environment expressions only.
2. Give every workflow a manual test trigger, correlation ID, bounded retries, and a failure route to WF-10.
3. Treat fetched text as untrusted data; never interpolate it into expressions that execute code.
4. Validate JSON structure and scan exports for tokens before completion.
5. Verify imports in a local n8n UI when available; otherwise mark external UI verification pending.

