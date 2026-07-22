"""
SQLAlchemy ORM models for repository storage.
All analysis results are stored as JSON text blobs for flexibility.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Repository(Base):
    """Represents a cloned and analyzed GitHub repository."""

    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    clone_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Analysis status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending | analyzing | complete | error
    progress: Mapped[int] = mapped_column(Integer, default=0)
    progress_message: Mapped[str] = mapped_column(String(500), default="")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Repository metadata (JSON)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    file_tree: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    file_analyses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    architecture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    documentation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    security_findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    quality_report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    health_score: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    learning_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    # Quick stats
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_folders: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    repo_size_mb: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
