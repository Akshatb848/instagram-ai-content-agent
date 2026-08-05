from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Source(TimestampMixin, Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    source_type: Mapped[str] = mapped_column(String(40))
    feed_url: Mapped[str] = mapped_column(String(2048), unique=True)
    authority_tier: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    items: Mapped[list["SourceItem"]] = relationship(back_populates="source")


class SourceItem(Base):
    __tablename__ = "source_items"
    __table_args__ = (UniqueConstraint("canonical_url"), UniqueConstraint("content_hash"))
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    title: Mapped[str] = mapped_column(String(500))
    canonical_url: Mapped[str] = mapped_column(String(2048))
    author: Mapped[str | None] = mapped_column(String(300))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    raw_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    source: Mapped[Source] = relationship(back_populates="items")


class TopicCandidate(Base):
    __tablename__ = "topic_candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    normalized_topic: Mapped[str] = mapped_column(String(500), unique=True)
    summary: Mapped[str] = mapped_column(Text)
    recency_score: Mapped[float] = mapped_column(Float, default=0)
    authority_score: Mapped[float] = mapped_column(Float, default=0)
    usefulness_score: Mapped[float] = mapped_column(Float, default=0)
    originality_score: Mapped[float] = mapped_column(Float, default=0)
    verification_score: Mapped[float] = mapped_column(Float, default=0)
    copyright_suitability_score: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    score_explanation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="NEW")


class Claim(Base):
    __tablename__ = "claims"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_candidate_id: Mapped[int] = mapped_column(ForeignKey("topic_candidates.id"))
    claim_text: Mapped[str] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(40))
    verification_status: Mapped[str] = mapped_column(String(40), default="PENDING")
    confidence: Mapped[float] = mapped_column(Float, default=0)
    risk_level: Mapped[str] = mapped_column(String(20))


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"))
    source_item_id: Mapped[int] = mapped_column(ForeignKey("source_items.id"))
    supporting_excerpt: Mapped[str] = mapped_column(Text)
    evidence_strength: Mapped[float] = mapped_column(Float)
    primary_source: Mapped[bool] = mapped_column(Boolean)
    source_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContentPackage(Base):
    __tablename__ = "content_packages"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic_candidate_id: Mapped[int] = mapped_column(ForeignKey("topic_candidates.id"))
    hook: Mapped[str] = mapped_column(String(300))
    narration_script: Mapped[str] = mapped_column(Text)
    caption: Mapped[str] = mapped_column(Text)
    hashtags_json: Mapped[list[str]] = mapped_column(JSON)
    scene_plan_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    source_disclosure_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    unsupported_claims_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    estimated_duration_seconds: Mapped[float] = mapped_column(Float)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(40), default="DRAFT")


class RenderJob(Base):
    __tablename__ = "render_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    content_package_id: Mapped[int] = mapped_column(ForeignKey("content_packages.id"))
    github_run_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    output_url: Mapped[str | None] = mapped_column(String(2048))
    checksum: Mapped[str | None] = mapped_column(String(64))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    validation_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text)


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    content_package_id: Mapped[int] = mapped_column(ForeignKey("content_packages.id"))
    telegram_message_id: Mapped[str] = mapped_column(String(100), unique=True)
    decision: Mapped[str] = mapped_column(String(30))
    feedback: Mapped[str | None] = mapped_column(Text)
    authorised_user_id: Mapped[str] = mapped_column(String(100))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Publication(Base):
    __tablename__ = "publications"
    __table_args__ = (UniqueConstraint("content_package_id", "platform"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    content_package_id: Mapped[int] = mapped_column(ForeignKey("content_packages.id"))
    platform: Mapped[str] = mapped_column(String(40), default="instagram")
    container_id: Mapped[str | None] = mapped_column(String(200))
    media_id: Mapped[str | None] = mapped_column(String(200))
    publication_status: Mapped[str] = mapped_column(String(40), default="PENDING")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    permalink: Mapped[str | None] = mapped_column(String(2048))
    error_message: Mapped[str | None] = mapped_column(Text)


class ContentMetric(Base):
    __tablename__ = "content_metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    views: Mapped[int | None] = mapped_column(Integer)
    reach: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    saves: Mapped[int | None] = mapped_column(Integer)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_name: Mapped[str] = mapped_column(String(100))
    correlation_id: Mapped[str] = mapped_column(String(100), unique=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40))
    error_code: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    usage_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
