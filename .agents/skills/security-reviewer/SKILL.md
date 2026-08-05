---
name: security-reviewer
description: Review this repository for secrets, dependency risk, SSRF, prompt injection, callback spoofing, unsafe subprocesses, duplicate publication, and least-privilege failures.
---

# Security review

1. Scan staged and tracked content for credentials and dangerous defaults.
2. Trace every untrusted input to network, filesystem, template, subprocess, and publication sinks.
3. Require allowlisted HTTP(S), public resolved IPs, redirect revalidation, size limits, MIME checks, and timeouts.
4. Require HMAC authentication, timestamp/expiry, constant-time comparison, nonce replay prevention, and idempotency.
5. Report evidence, severity, exploit condition, fix, and test. Do not suppress credible findings to pass a gate.

