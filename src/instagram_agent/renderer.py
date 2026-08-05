import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class RenderSpec:
    background: Path
    audio: Path
    subtitles: Path
    output: Path
    watermark: str
    duration_seconds: float


def ffmpeg_command(spec: RenderSpec) -> list[str]:
    if not 0 < spec.duration_seconds <= 60:
        raise ValueError("Duration must be within 60 seconds")
    escaped_subs = str(spec.subtitles).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    escaped_mark = spec.watermark.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    filters = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"subtitles='{escaped_subs}',drawtext=text='{escaped_mark}':"
        "x=w-tw-60:y=60:fontsize=32:fontcolor=white@0.8"
    )
    return [
        "ffmpeg",
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(spec.background),
        "-i",
        str(spec.audio),
        "-t",
        f"{spec.duration_seconds:.3f}",
        "-vf",
        filters,
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-movflags",
        "+faststart",
        "-shortest",
        str(spec.output),
    ]


def run_render(spec: RenderSpec, timeout: int = 600) -> None:
    subprocess.run(  # noqa: S603 - executable is a fixed literal; arguments are not shelled
        ffmpeg_command(spec), check=True, timeout=timeout, capture_output=True
    )


def write_srt(sentences: list[tuple[float, float, str]], path: Path) -> None:
    def stamp(value: float) -> str:
        millis = round(value * 1000)
        hours, rem = divmod(millis, 3_600_000)
        minutes, rem = divmod(rem, 60_000)
        seconds, ms = divmod(rem, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

    blocks = [
        f"{index}\n{stamp(start)} --> {stamp(end)}\n{text.strip()}"
        for index, (start, end, text) in enumerate(sentences, 1)
    ]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def probe(path: Path) -> dict[str, Any]:
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    result = subprocess.run(  # noqa: S603 - executable is a fixed literal
        command, check=True, timeout=30, capture_output=True, text=True
    )
    return cast(dict[str, Any], json.loads(result.stdout))


def validate_probe(data: dict[str, Any], max_seconds: float = 60) -> dict[str, Any]:
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    duration = float(data.get("format", {}).get("duration", 0))
    errors: list[str] = []
    if (
        not video
        or video.get("width") != 1080
        or video.get("height") != 1920
        or video.get("codec_name") != "h264"
    ):
        errors.append("Invalid video stream")
    if not audio or audio.get("codec_name") != "aac":
        errors.append("Invalid audio stream")
    if duration <= 0 or duration > max_seconds:
        errors.append("Invalid duration")
    return {"valid": not errors, "errors": errors, "duration": duration}


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(spec: RenderSpec, validation: dict[str, Any], path: Path) -> None:
    payload = asdict(spec)
    payload = {
        key: str(value) if isinstance(value, Path) else value for key, value in payload.items()
    }
    payload["validation"] = validation
    payload["output_sha256"] = checksum(spec.output)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
