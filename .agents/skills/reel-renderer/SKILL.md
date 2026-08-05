---
name: reel-renderer
description: Build and verify this project's deterministic FFmpeg Reel renderer, subtitle layouts, safe areas, cover images, manifests, checksums, and ffprobe validation.
---

# Reel rendering

1. Construct subprocess argument arrays; never use `shell=True` or untrusted filter fragments.
2. Produce H.264/AAC MP4 at 1080x1920, 30 fps, at most 60 seconds, with fast-start.
3. Keep subtitle and watermark text inside configured safe margins; escape ASS separately from shell arguments.
4. Record asset license, origin, checksum, command plan, timing, and output checksum in the manifest.
5. Fail closed when ffprobe reports wrong streams, dimensions, codecs, duration, or empty output.

