#!/usr/bin/env python3
"""Seed the database with sample jobs and embeddings."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.job import Job
from app.services.semantic_search import SemanticSearchService


SAMPLE_JOBS = [
    {
        "external_id": "gh-1",
        "title": "Senior Machine Learning Engineer",
        "company": "Anthropic",
        "location": "San Francisco, CA",
        "description": (
            "We're looking for a Senior ML Engineer to help build safe, steerable, and "
            "interpretable AI systems. You'll work on large language model training, "
            "alignment techniques, and evaluation frameworks. Experience with PyTorch, "
            "distributed training, and transformer architectures required."
        ),
        "url": "https://anthropic.com/careers/senior-ml-engineer",
        "source": "company",
        "skills": ["python", "pytorch", "transformers", "distributed systems", "machine learning"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 200000,
        "salary_max": 350000,
        "currency": "USD",
    },
    {
        "external_id": "gh-2",
        "title": "Backend Engineer - AI Infrastructure",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "description": (
            "Build and scale the infrastructure that powers our AI models. "
            "Work on high-throughput serving, training clusters, and developer APIs. "
            "Strong Python, Rust, or Go skills. Experience with Kubernetes, "
            "distributed systems, and GPU workloads."
        ),
        "url": "https://openai.com/careers/backend-ai-infra",
        "source": "company",
        "skills": ["python", "rust", "go", "kubernetes", "distributed systems", "gpu"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 180000,
        "salary_max": 300000,
        "currency": "USD",
    },
    {
        "external_id": "gh-3",
        "title": "Full Stack Engineer",
        "company": "Vercel",
        "location": "Remote (US)",
        "description": (
            "Join the team building the frontend cloud. Work on Next.js, "
            "edge functions, and developer experience tools. React, TypeScript, "
            "and modern web platform expertise required."
        ),
        "url": "https://vercel.com/careers/fullstack",
        "source": "company",
        "skills": ["typescript", "react", "next.js", "node.js", "edge computing"],
        "seniority": "mid",
        "employment_type": "full-time",
        "salary_min": 150000,
        "salary_max": 250000,
        "currency": "USD",
    },
    {
        "external_id": "gh-4",
        "title": "DevOps Engineer",
        "company": "Datadog",
        "location": "New York, NY",
        "description": (
            "Scale monitoring infrastructure to handle millions of hosts. "
            "Work on Kubernetes, Kafka, and distributed tracing. "
            "Go, Python, and cloud provider expertise."
        ),
        "url": "https://datadog.com/careers/devops",
        "source": "company",
        "skills": ["go", "kubernetes", "kafka", "distributed tracing", "aws", "python"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 160000,
        "salary_max": 240000,
        "currency": "USD",
    },
    {
        "external_id": "gh-5",
        "title": "Data Scientist - NLP",
        "company": "Hugging Face",
        "location": "Remote (Global)",
        "description": (
            "Advance the state of open-source NLP. Work on transformers, "
            "datasets, and model evaluation. Publish research, contribute to "
            "open-source libraries. PhD or equivalent experience."
        ),
        "url": "https://huggingface.co/careers/data-scientist-nlp",
        "source": "company",
        "skills": ["python", "pytorch", "transformers", "nlp", "hugging face", "research"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 140000,
        "salary_max": 220000,
        "currency": "USD",
    },
    {
        "external_id": "gh-6",
        "title": "Frontend Engineer",
        "company": "Linear",
        "location": "Remote (US/CA)",
        "description": (
            "Build a beautiful, fast issue tracker. React, TypeScript, "
            "electron, and real-time sync. Obsess over craft and performance."
        ),
        "url": "https://linear.app/careers/frontend",
        "source": "company",
        "skills": ["typescript", "react", "electron", "real-time", "design systems"],
        "seniority": "mid",
        "employment_type": "full-time",
        "salary_min": 130000,
        "salary_max": 200000,
        "currency": "USD",
    },
    {
        "external_id": "gh-7",
        "title": "ML Research Engineer",
        "company": "DeepMind",
        "location": "London, UK",
        "description": (
            "Fundamental research in deep learning and reinforcement learning. "
            "Publish at top conferences. JAX, TPU, large-scale experiments."
        ),
        "url": "https://deepmind.com/careers/ml-research",
        "source": "company",
        "skills": ["python", "jax", "deep learning", "reinforcement learning", "research", "tpu"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 120000,
        "salary_max": 280000,
        "currency": "GBP",
    },
    {
        "external_id": "gh-8",
        "title": "Platform Engineer",
        "company": "Temporal",
        "location": "Seattle, WA",
        "description": (
            "Build durable execution for distributed applications. Go, gRPC, "
            "databases, and workflow engines. Open-source first."
        ),
        "url": "https://temporal.io/careers/platform",
        "source": "company",
        "skills": ["go", "grpc", "distributed systems", "databases", "workflow engines"],
        "seniority": "senior",
        "employment_type": "full-time",
        "salary_min": 170000,
        "salary_max": 260000,
        "currency": "USD",
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(Job).count()
        if existing > 0:
            print(f"Database already has {existing} jobs. Skipping seed.")
            return

        print("Generating embeddings for sample jobs...")
        # Prepare texts for embedding: title + company + description + skills
        texts = []
        for job_data in SAMPLE_JOBS:
            skill_text = " ".join(job_data.get("skills", []))
            text = f"{job_data['title']} at {job_data['company']}. {job_data['description']}. Skills: {skill_text}"
            texts.append(text)

        embeddings = SemanticSearchService.encode(texts)

        print("Inserting jobs with embeddings...")
        for job_data, embedding in zip(SAMPLE_JOBS, embeddings):
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
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                currency=job_data["currency"],
                embedding=embedding.tolist(),
            )
            db.add(job)

        db.commit()
        print(f"Seeded {len(SAMPLE_JOBS)} jobs successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()