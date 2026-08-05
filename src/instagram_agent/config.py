from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./instagram_agent.db"
    llm_provider: Literal["mock", "gemini", "ollama"] = "mock"
    gemini_model: str = "gemini-2.5-flash-lite"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = ""
    max_reels_per_week: int = Field(3, ge=0, le=3)
    max_source_items_per_run: int = Field(30, ge=1, le=30)
    max_llm_retries: int = Field(2, ge=0, le=2)
    max_render_attempts: int = Field(2, ge=1, le=2)
    max_video_seconds: int = Field(60, ge=30, le=60)
    max_concurrent_render_jobs: int = Field(1, ge=1, le=1)
    auto_publish: bool = False
    cloud_media_retention_days: int = Field(7, ge=1, le=7)
    github_artifact_retention_days: int = Field(3, ge=1, le=3)
    allow_paid_fallback: bool = False
    verification_threshold: float = Field(0.8, ge=0, le=1)
    brand_username: str = "@yourhandle"

    @model_validator(mode="after")
    def fail_closed(self) -> "Settings":
        if self.auto_publish:
            raise ValueError("AUTO_PUBLISH must remain false; publication requires approval")
        if self.allow_paid_fallback:
            raise ValueError("Paid fallback is prohibited")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
