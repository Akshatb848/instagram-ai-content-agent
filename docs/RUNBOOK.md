# Operations runbook

Daily: inspect failed workflow runs and Telegram alerts. Weekly: review quotas, expired assets, dependency alerts, and backup success. Monthly: test a restore and confirm provider free-tier terms.

Incident response: disable workflow activation, preserve correlation IDs and redacted logs, rotate affected credentials, assess duplicate-publication state, fix with tests, then reactivate one workflow at a time. Never bypass approval or verification to clear a queue.

