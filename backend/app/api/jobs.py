from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.job import Job

router = APIRouter(prefix="/api", tags=["jobs"])


class JobResponse(BaseModel):
    id: int
    external_id: str
    title: str
    company: str
    location: Optional[str]
    description: str
    url: str
    source: str
    posted_at: Optional[str]
    fetched_at: Optional[str]
    skills: List[str]
    seniority: Optional[str]
    employment_type: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    currency: Optional[str]

    class Config:
        from_attributes = True


class JobsListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


@router.get("/jobs", response_model=JobsListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    company: Optional[str] = None,
    location: Optional[str] = None,
    seniority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if seniority:
        query = query.filter(Job.seniority == seniority)
    
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    jobs = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return JobsListResponse(
        jobs=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.get("/jobs/external/{external_id}", response_model=JobResponse)
def get_job_by_external_id(external_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.external_id == external_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)