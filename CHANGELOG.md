# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-23

### Added
- FastAPI backend with SQLite persistence
- Semantic job search using sentence-transformers (all-MiniLM-L6-v2)
- Search API with filters (location, seniority, employment type) and pagination
- Dictionary coverage checker for skills, roles, industries (canonical/alias/miss)
- Dictionary submission endpoint with deduplication counter
- React + TypeScript + Vite frontend
- Search page with query input, filters, URL-synced state
- JobCard component with match score, skills, salary, expandable explanation
- Dictionary coverage panel in UI
- Unit tests for semantic search, dictionary service, and API endpoints
- Frontend component tests for JobCard
- Seed script with 8 sample jobs and precomputed embeddings
- Dockerfiles and docker-compose for full-stack deployment
- README with architecture diagram, API reference, AI/ML evaluation
- MIT license

### AI/ML
- Semantic similarity ranking using cosine similarity on normalized embeddings
- Match score thresholds: high (≥0.7), medium (≥0.4), low (<0.4)
- Human-readable match explanations generated from job metadata

### Security
- CORS configured for local development only
- No authentication (demo mode)
- SQLite file-based storage
- No rate limiting