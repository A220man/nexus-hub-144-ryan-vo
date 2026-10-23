from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False)
    source = Column(String(100), nullable=False)
    posted_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(SQLiteJSON, nullable=True)  # Stored as list[float]
    skills = Column(SQLiteJSON, nullable=True)  # List[str]
    seniority = Column(String(50), nullable=True)
    employment_type = Column(String(50), nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(String(10), nullable=True)

    __table_args__ = (
        Index("ix_jobs_title_company", "title", "company"),
        Index("ix_jobs_location", "location"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "skills": self.skills or [],
            "seniority": self.seniority,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
        }


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String(500), nullable=False)
    location = Column(String(255), nullable=True)
    filters = Column(SQLiteJSON, nullable=True)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), nullable=True)  # For future auth integration


class DictionaryCoverageRequest(Base):
    __tablename__ = "dictionary_coverage_requests"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(50), nullable=False)  # skill, role, industry
    raw_term = Column(String(500), nullable=False)
    normalized_term = Column(String(500), nullable=False, index=True)
    request_count = Column(Integer, default=1)
    first_requested_at = Column(DateTime, default=datetime.utcnow)
    last_requested_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_by = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    resolution_note = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_dictionary_kind_normalized", "kind", "normalized_term", unique=True),
    )