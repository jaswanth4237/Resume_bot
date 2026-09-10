import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(String, unique=True, nullable=True, index=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = relationship("AnalysisSession", back_populates="user", cascade="all, delete-orphan")


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="sessions")
    job_description = relationship("JobDescriptionModel", back_populates="session", uselist=False)
    resumes = relationship("ResumeModel", back_populates="session")
    match_results = relationship("MatchResultModel", back_populates="session")


class JobDescriptionModel(Base):
    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("analysis_sessions.id"))
    filename = Column(String)
    title = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    extracted_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AnalysisSession", back_populates="job_description")


class ResumeModel(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("analysis_sessions.id"))
    filename = Column(String)
    candidate_name = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    extracted_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AnalysisSession", back_populates="resumes")


class MatchResultModel(Base):
    __tablename__ = "match_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("analysis_sessions.id"))
    overall_score = Column(Float)
    decision = Column(String)
    result_json = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AnalysisSession", back_populates="match_results")
