import os
import uuid


def main() -> None:
    job_id = uuid.UUID(os.environ["RENDER_JOB_ID"])
    required = ["N8N_JOB_ENDPOINT", "GITHUB_CALLBACK_SECRET", "CLOUDINARY_URL"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing required render integration configuration")
    raise RuntimeError(
        f"Render job {job_id} requires a configured signed n8n fetch endpoint; "
        "live execution is intentionally blocked until credentials are supplied"
    )


if __name__ == "__main__":
    main()
