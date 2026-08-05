from pathlib import Path

import pytest

from instagram_agent.renderer import (
    RenderSpec,
    checksum,
    ffmpeg_command,
    validate_probe,
    write_manifest,
    write_srt,
)


def test_render_command_is_argument_array(tmp_path: Path) -> None:
    spec = RenderSpec(
        tmp_path / "bg.mp4",
        tmp_path / "voice.wav",
        tmp_path / "sub.srt",
        tmp_path / "out.mp4",
        "@brand",
        30,
    )
    command = ffmpeg_command(spec)
    assert command[0] == "ffmpeg"
    assert "shell=True" not in command
    assert "1080:1920" in command[command.index("-vf") + 1]


def test_subtitle_timing(tmp_path: Path) -> None:
    output = tmp_path / "test.srt"
    write_srt([(0, 1.25, "Hello")], output)
    assert "00:00:00,000 --> 00:00:01,250" in output.read_text(encoding="utf-8")


def test_probe_validation() -> None:
    data = {
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_type": "audio", "codec_name": "aac"},
        ],
        "format": {"duration": "30.0"},
    }
    assert validate_probe(data)["valid"] is True
    data["format"]["duration"] = "61"
    assert validate_probe(data)["valid"] is False


def test_checksum_and_manifest(tmp_path: Path) -> None:
    output = tmp_path / "out.mp4"
    output.write_bytes(b"synthetic-video")
    spec = RenderSpec(
        tmp_path / "bg.mp4",
        tmp_path / "voice.wav",
        tmp_path / "sub.srt",
        output,
        "@brand",
        30,
    )
    manifest = tmp_path / "manifest.json"
    write_manifest(spec, {"valid": True}, manifest)
    assert checksum(output) in manifest.read_text(encoding="utf-8")


def test_invalid_duration_and_video_probe(tmp_path: Path) -> None:
    spec = RenderSpec(
        tmp_path / "bg.mp4",
        tmp_path / "voice.wav",
        tmp_path / "sub.srt",
        tmp_path / "out.mp4",
        "@brand",
        61,
    )
    with pytest.raises(ValueError, match="Duration"):
        ffmpeg_command(spec)
    assert validate_probe({"streams": [], "format": {"duration": "0"}})["valid"] is False
