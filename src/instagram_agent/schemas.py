from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


class EvidenceRef(BaseModel):
    claim: str
    url: HttpUrl
    excerpt: str = Field(max_length=500)
    primary_source: bool
    confidence: float = Field(ge=0, le=1)


class Scene(BaseModel):
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0, le=60)
    narration: str
    on_screen_text: str = Field(max_length=100)
    visual_type: Literal["video", "image", "kinetic_text"]
    asset_url: HttpUrl | None = None
    asset_attribution: str | None = None

    @model_validator(mode="after")
    def ordered(self) -> "Scene":
        if self.end_seconds <= self.start_seconds:
            raise ValueError("Scene end must follow start")
        return self


class ReelPackage(BaseModel):
    topic: str
    target_audience_level: Literal["beginner", "intermediate", "advanced"]
    reel_objective: str
    hook: str = Field(max_length=160)
    narration_script: str
    estimated_duration_seconds: float = Field(ge=30, le=60)
    scenes: list[Scene] = Field(min_length=1)
    caption: str = Field(max_length=2200)
    hashtags: list[str] = Field(min_length=1, max_length=20)
    source_disclosures: list[HttpUrl]
    claims: list[str]
    evidence: list[EvidenceRef]
    unsupported_claims: list[str]
    confidence: float = Field(ge=0, le=1)
    safety_notes: list[str]

    @model_validator(mode="after")
    def publication_gate(self) -> "ReelPackage":
        if self.unsupported_claims:
            raise ValueError("Unsupported claims block the package")
        if max(scene.end_seconds for scene in self.scenes) > self.estimated_duration_seconds:
            raise ValueError("Scene plan exceeds estimated duration")
        return self
