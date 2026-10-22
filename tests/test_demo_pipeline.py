"""Runs scripts/demo_pipeline.py end to end (offline, synthetic inputs).

The FFmpeg render assertions are skipped when ffmpeg/ffprobe are not installed;
CI installs FFmpeg so they run there.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from instagram_agent.renderer import probe, validate_probe

ROOT = Path(__file__).resolve().parents[1]
HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def run_demo(out: Path) -> str:
    result = subprocess.run(  # noqa: S603 - fixed interpreter and script path
        [sys.executable, str(ROOT / "scripts" / "demo_pipeline.py"), "--out", str(out)],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.stdout


def test_demo_enforces_gates(tmp_path: Path) -> None:
    output = run_demo(tmp_path)
    assert "AUTO_PUBLISH=true -> rejected at startup" in output
    assert "repost is duplicate: True" in output
    assert "injected item rejected" in output
    assert "publishable=False" in output
    assert "replayed callback rejected" in output or not HAS_FFMPEG


@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg/ffprobe not installed")
def test_demo_renders_valid_vertical_reel(tmp_path: Path) -> None:
    output = run_demo(tmp_path)
    reel = tmp_path / "reel.mp4"
    assert reel.exists()
    validation = validate_probe(probe(reel))
    assert validation == {"valid": True, "errors": [], "duration": pytest.approx(8.0, abs=0.2)}
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["output_sha256"]) == 64
    assert "second publish rejected" in output
