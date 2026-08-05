FROM python:3.11.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg=7:5.1.7-0+deb12u1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.lock ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 renderer
USER renderer
ENTRYPOINT ["python", "-m", "instagram_agent"]

