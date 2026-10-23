# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-search

## Roadmap

### core-search — Core job search with AI-powered semantic matching

Status: done

Acceptance:
- Backend serves /api/search endpoint accepting query, location, filters
- Frontend search page renders results with pagination
- Semantic matching uses sentence-transformers for query-job embedding similarity
- Results include AI match score and explanation

Implementation: `backend/app/main.py`, `backend/app/api/search.py`, `backend/app/services/semantic_search.py`, `backend/app/models/job.py`, `frontend/src/pages/Search.tsx`, `frontend/src/components/JobCard.tsx`, `frontend/src/api/client.ts`

Tests: `backend/tests/test_search.py`, `frontend/src/components/__tests__/JobCard.test.tsx`

### dictionary-coverage — Dictionary coverage checker for skills/roles/industries

Status: planned

Acceptance:
- Public /dictionary page with search input
- Three result types: canonical hit, alias hit, miss
- Misses recorded with deduplication counter for admin review

### profile-redesign — Redesigned candidate profile page (single-page, autosave)

Status: planned

Acceptance:
- Single scrolling page replaces 8 tabs
- Unified autosave across all sections
- Profile completeness indicator at top

### anonymous-tracking — Anonymous application process sharing with k-anonymity

Status: planned

Acceptance:
- Opt-in per-job sharing toggle
- Aggregates shown only when k>=5
- Stage timing and outcome distributions displayed

