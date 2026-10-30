import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal, engine, Base
from app.models.job import Job
from app.services.semantic_search import SemanticSearchService

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    existing = db.query(Job).count()
    if existing == 0:
        texts = []
        job_data_list = [
            {
                "external_id": "test-1",
                "title": "ML Engineer",
                "company": "TestCorp",
                "location": "Remote",
                "description": "Machine learning with PyTorch and transformers",
                "url": "https://test.com/1",
                "source": "test",
                "skills": ["python", "pytorch", "machine learning"],
                "seniority": "senior",
                "employment_type": "full-time",
            },
            {
                "external_id": "test-2",
                "title": "Frontend Developer",
                "company": "WebCo",
                "location": "NYC",
                "description": "React and TypeScript frontend work",
                "url": "https://test.com/2",
                "source": "test",
                "skills": ["typescript", "react", "frontend"],
                "seniority": "mid",
                "employment_type": "full-time",
            },
            {
                "external_id": "test-3",
                "title": "Backend Engineer",
                "company": "DataSys",
                "location": "San Francisco",
                "description": "Python backend development with FastAPI and PostgreSQL",
                "url": "https://test.com/3",
                "source": "test",
                "skills": ["python", "fastapi", "postgresql", "backend"],
                "seniority": "senior",
                "employment_type": "full-time",
            },
            {
                "external_id": "test-4",
                "title": "Data Scientist",
                "company": "AIStartup",
                "location": "Remote",
                "description": "Statistical modeling and ML pipelines with scikit-learn",
                "url": "https://test.com/4",
                "source": "test",
                "skills": ["python", "scikit-learn", "statistics", "data science"],
                "seniority": "mid",
                "employment_type": "full-time",
            },
            {
                "external_id": "test-5",
                "title": "DevOps Engineer",
                "company": "CloudCorp",
                "location": "Austin",
                "description": "Kubernetes and AWS infrastructure automation",
                "url": "https://test.com/5",
                "source": "test",
                "skills": ["kubernetes", "aws", "docker", "terraform"],
                "seniority": "senior",
                "employment_type": "full-time",
            },
        ]
        for job_data in job_data_list:
            skill_text = " ".join(job_data.get("skills", []))
            text = f"{job_data['title']} at {job_data['company']}. {job_data['description']}. Skills: {skill_text}"
            texts.append(text)

        embeddings = SemanticSearchService.encode(texts)
        for job_data, emb in zip(job_data_list, embeddings):
            job = Job(
                external_id=job_data["external_id"],
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"],
                url=job_data["url"],
                source=job_data["source"],
                skills=job_data["skills"],
                seniority=job_data["seniority"],
                employment_type=job_data["employment_type"],
                embedding=emb.tolist(),
            )
            db.add(job)
        db.commit()
        print(f"Seeded {len(job_data_list)} jobs")
    else:
        print(f"Database already has {existing} jobs")
finally:
    db.close()
