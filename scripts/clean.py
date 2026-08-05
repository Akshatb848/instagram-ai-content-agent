from pathlib import Path
from time import time


def main() -> None:
    root = Path("artifacts")
    cutoff = time() - 3 * 86400
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink()


if __name__ == "__main__":
    main()
