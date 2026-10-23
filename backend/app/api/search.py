from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import numpy as np

from app.core.database import get_db
from app.models.job import Job, SearchQuery, DictionaryCoverageRequest
from app.services.semantic_search import SemanticSearchService, DictionaryService
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    seniority: Optional[str] = None
    employment_type: Optional[str] = None
    page: int = 1
    per_page: int = 20


class SearchResult(BaseModel):
    job: Dict[str, Any]
    match_score: float
    match_explanation: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    per_page: int
    total_pages: int


class DictionaryCheckRequest(BaseModel):
    term: str
    kind: str  # skill, role, industry


class DictionaryCheckResponse(BaseModel):
    type: str  # canonical, alias, miss
    canonical: Optional[str] = None
    display: Optional[str] = None
    term: str
    kind: str


class DictionarySubmitRequest(BaseModel):
    term: str
    kind: str


@router.post("/search", response_model=SearchResponse)
def search_jobs(request: SearchRequest, db: Session = Depends(get_db)):
    # Build base query
    query = db.query(Job)

    # Apply filters
    if request.location:
        query = query.filter(Job.location.ilike(f"%{request.location}%"))
    if request.seniority:
        query = query.filter(Job.seniority == request.seniority)
    if request.employment_type:
        query = query.filter(Job.employment_type == request.employment_type)
    if request.skills:
        # Simple JSON contains check for SQLite
        for skill in request.skills:
            query = query.filter(Job.skills.contains([skill]))

    # Get all matching jobs for semantic ranking
    jobs = query.all()

    # Semantic ranking
    query_embedding = SemanticSearchService.encode_single(request.query)

    results = []
    for job in jobs:
        score = SemanticSearchService.compute_match_score(query_embedding, job.embedding or [])
        explanation = SemanticSearchService.generate_match_explanation(request.query, job.to_dict(), score)
        results.append(SearchResult(
            job=job.to_dict(),
            match_score=score,
            match_explanation=explanation
        ))

    # Sort by match score descending
    results.sort(key=lambda r: r.match_score, reverse=True)

    # Pagination
    total = len(results)
    total_pages = (total + request.per_page - 1) // request.per_page
    start = (request.page - 1) * request.per_page
    end = start + request.per_page
    paginated = results[start:end]

    # Log search query
    search_log = SearchQuery(
        query_text=request.query,
        location=request.location,
        filters=request.model_dump(exclude={"query", "page", "per_page"}),
        results_count=total,
    )
    db.add(search_log)
    db.commit()

    return SearchResponse(
        results=paginated,
        total=total,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
    )


@router.post("/dictionary/check", response_model=DictionaryCheckResponse)
def check_dictionary_coverage(request: DictionaryCheckRequest):
    result = DictionaryService.check_coverage(request.term, request.kind)
    return DictionaryCheckResponse(
        **result,
        term=request.term,
        kind=request.kind,
    )


@router.post("/dictionary/submit")
def submit_dictionary_request(request: DictionarySubmitRequest, db: Session = Depends(get_db)):
    normalized = DictionaryService.normalize_term(request.term, request.kind)

    # Check for existing entry
    existing = db.query(DictionaryCoverageRequest).filter(
        DictionaryCoverageRequest.kind == request.kind,
        DictionaryCoverageRequest.normalized_term == normalized,
    ).first()

    if existing:
        existing.request_count += 1
        existing.last_requested_at = __import__("datetime").datetime.utcnow()
        db.commit()
        return {"status": "updated", "request_count": existing.request_count, "id": existing.id}

    # Create new entry
    entry = DictionaryCoverageRequest(
        kind=request.kind,
        raw_term=request.term,
        normalized_term=normalized,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"status": "created", "id": entry.id, "request_count": 1}


@router.get("/dictionary/pending")
def get_pending_dictionary_requests(
    kind: Optional[str] = None,
    status: str = "pending",
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(DictionaryCoverageRequest).filter(
        DictionaryCoverageRequest.status == status
    )
    if kind:
        query = query.filter(DictionaryCoverageRequest.kind == kind)
    query = query.order_by(DictionaryCoverageRequest.request_count.desc())
    results = query.limit(limit).all()

    return [
        {
            "id": r.id,
            "kind": r.kind,
            "raw_term": r.raw_term,
            "normalized_term": r.normalized_term,
            "request_count": r.request_count,
            "first_requested_at": r.first_requested_at.isoformat(),
            "last_requested_at": r.last_requested_at.isoformat(),
            "submitted_by": r.submitted_by,
            "status": r.status,
            "resolution_note": r.resolution_note,
        }
        for r in results
    ]