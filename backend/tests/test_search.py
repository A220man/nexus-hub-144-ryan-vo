import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal, engine, Base
from app.models.job import Job, SearchQuery, DictionaryCoverageRequest
from app.services.semantic_search import SemanticSearchService, DictionaryService


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="module", autouse=True)
def seed_db():
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
    finally:
        db.close()


class TestSemanticSearchService:
    def test_encode_returns_normalized_vectors(self):
        texts = ["hello world", "machine learning"]
        embeddings = SemanticSearchService.encode(texts)
        assert embeddings.shape == (2, 384)  # all-MiniLM-L6-v2 dimension
        norms = np.linalg.norm(embeddings, axis=1)
        assert all(abs(n - 1.0) < 1e-5 for n in norms)

    def test_cosine_similarity_identical(self):
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert SemanticSearchService.cosine_similarity(a, b) == 1.0

    def test_cosine_similarity_orthogonal(self):
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        assert SemanticSearchService.cosine_similarity(a, b) == 0.0

    def test_compute_match_score_empty_embedding(self):
        query_emb = SemanticSearchService.encode_single("test")
        assert SemanticSearchService.compute_match_score(query_emb, []) == 0.0
        assert SemanticSearchService.compute_match_score(query_emb, [0.0] * 384) == 0.0


class TestDictionaryService:
    def test_canonical_skill_hit(self):
        result = DictionaryService.check_coverage("python", "skill")
        assert result["type"] == "canonical"
        assert result["canonical"] == "python"

    def test_alias_skill_hit(self):
        result = DictionaryService.check_coverage("k8s", "skill")
        assert result["type"] == "alias"
        assert result["canonical"] == "kubernetes"

    def test_alias_role_hit(self):
        result = DictionaryService.check_coverage("swe", "role")
        assert result["type"] == "alias"
        assert result["canonical"] == "software engineer"

    def test_alias_industry_hit(self):
        result = DictionaryService.check_coverage("fintech", "industry")
        assert result["type"] == "alias"
        assert result["canonical"] == "financial technology"

    def test_miss(self):
        result = DictionaryService.check_coverage("quantum knitting", "skill")
        assert result["type"] == "miss"
        assert result["canonical"] is None

    def test_normalize_term(self):
        assert DictionaryService.normalize_term("K8S", "skill") == "kubernetes"
        assert DictionaryService.normalize_term("ReactJS", "skill") == "react"
        assert DictionaryService.normalize_term("SWE", "role") == "software engineer"
        assert DictionaryService.normalize_term("FinTech", "industry") == "financial technology"
        assert DictionaryService.normalize_term("unknown term", "skill") == "unknown term"


class TestSearchAPI:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "nexus-hub"
        assert "version" in data

    def test_search_endpoint_exists(self, client):
        response = client.post("/api/search", json={"query": "machine learning"})
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "page" in data
        assert "total_pages" in data

    def test_search_with_filters(self, client):
        response = client.post("/api/search", json={
            "query": "python",
            "location": "San Francisco",
            "seniority": "senior",
            "page": 1,
            "per_page": 10,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_dictionary_check_canonical(self, client):
        response = client.post("/api/dictionary/check", json={"term": "python", "kind": "skill"})
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "canonical"
        assert data["canonical"] == "python"

    def test_dictionary_check_alias(self, client):
        response = client.post("/api/dictionary/check", json={"term": "k8s", "kind": "skill"})
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "alias"
        assert data["canonical"] == "kubernetes"

    def test_dictionary_check_miss(self, client):
        response = client.post("/api/dictionary/check", json={"term": "xyz123unknown", "kind": "skill"})
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "miss"

    def test_dictionary_submit_creates_entry(self, client):
        response = client.post("/api/dictionary/submit", json={"term": "rust async", "kind": "skill"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["request_count"] == 1

    def test_dictionary_submit_deduplicates(self, client):
        client.post("/api/dictionary/submit", json={"term": "go generics", "kind": "skill"})
        response = client.post("/api/dictionary/submit", json={"term": "go generics", "kind": "skill"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["request_count"] == 2

    def test_dictionary_pending_endpoint(self, client):
        response = client.get("/api/dictionary/pending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)