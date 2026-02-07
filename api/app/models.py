from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    script = relationship("Script", back_populates="project", uselist=False)
    dialogues = relationship("Dialogue", back_populates="project", cascade="all, delete-orphan")
    shots = relationship("Shot", back_populates="project", cascade="all, delete-orphan")
    renders = relationship("Render", back_populates="project", cascade="all, delete-orphan")
    settings = relationship("ProjectSettings", back_populates="project", uselist=False, cascade="all, delete-orphan")


class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="script")


class Dialogue(Base):
    __tablename__ = "dialogues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    speaker: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="dialogues")


class Shot(Base):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    shot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, default=3)

    project = relationship("Project", back_populates="shots")


class Render(Base):
    __tablename__ = "renders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    status: Mapped[str] = mapped_column(String(50), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    output_video_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="renders")


class ProjectSettings(Base):
    __tablename__ = "project_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    avatar_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    voice_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_iv_image_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    background_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    use_shots_for_avatar_iv: Mapped[int] = mapped_column(Integer, default=1)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tts_provider: Mapped[str] = mapped_column(String(50), default="aliyun")
    enable_heygen: Mapped[int] = mapped_column(Integer, default=1)
    enable_avatar_iv: Mapped[int] = mapped_column(Integer, default=1)

    project = relationship("Project", back_populates="settings")
