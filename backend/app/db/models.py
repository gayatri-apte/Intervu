from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
)

from app.db.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    duration = Column(
        Float,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="created",
    )


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    question_id = Column(
        String,
        nullable=True,
    )

    speaker = Column(
        String,
        nullable=False,
    )

    start_time = Column(
        Float,
        nullable=False,
    )

    end_time = Column(
        Float,
        nullable=False,
    )

    text = Column(
        Text,
        nullable=False,
    )


class QuestionResult(Base):
    __tablename__ = "question_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    question_id = Column(
        String,
        nullable=False,
    )

    relevance = Column(
        Float,
        nullable=True,
    )

    star_structure = Column(
        Float,
        nullable=True,
    )

    completeness = Column(
        Float,
        nullable=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )


class ProsodyMetric(Base):
    __tablename__ = "prosody_metrics"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
    )

    question_id = Column(
        String,
        nullable=True,
    )

    wpm = Column(
        Float,
        nullable=True,
    )

    filler_word_count = Column(
        Integer,
        nullable=True,
    )

    pause_count = Column(
        Integer,
        nullable=True,
    )

    pause_duration = Column(
        Float,
        nullable=True,
    )

    pitch_variance = Column(
        Float,
        nullable=True,
    )