from dataclasses import dataclass

from instagram_agent.config import Settings


class FreeTierQuotaExhausted(RuntimeError):
    code = "FREE_TIER_QUOTA_EXHAUSTED"


@dataclass(frozen=True)
class Usage:
    reels_this_week: int
    source_items_this_run: int
    active_render_jobs: int


def enforce(settings: Settings, usage: Usage) -> None:
    if usage.reels_this_week >= settings.max_reels_per_week:
        raise FreeTierQuotaExhausted("Weekly Reel quota exhausted")
    if usage.source_items_this_run > settings.max_source_items_per_run:
        raise FreeTierQuotaExhausted("Source-item quota exhausted")
    if usage.active_render_jobs >= settings.max_concurrent_render_jobs:
        raise FreeTierQuotaExhausted("Render concurrency quota exhausted")
