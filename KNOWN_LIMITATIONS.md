# Known limitations

- Live integrations are intentionally unverified without credentials.
- n8n workflow exports import successfully and establish the versioned topology and triggers; detailed credentialed operational nodes still require implementation and sandbox iteration.
- The renderer command, subtitles, manifests, checksum, and probe validator are tested, but a full Piper-to-MP4 synthetic render is still pending.
- Local PyPI vulnerability querying is blocked by the machine's TLS certificate-chain configuration; Ubuntu CI carries the audit gate.
- Cloud Run is documented only as an optional alternative; the default deployment is e2-micro plus GitHub Actions.
