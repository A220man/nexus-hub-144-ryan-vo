import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api, SearchRequest, SearchResponse, SearchResult, DictionaryCheckResponse } from '../api/client';
import { JobCard } from '../components/JobCard';

const SENIORITY_OPTIONS = ['', 'junior', 'mid', 'senior', 'lead', 'principal'];
const EMPLOYMENT_TYPES = ['', 'full-time', 'part-time', 'contract', 'internship'];

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [location, setLocation] = useState(searchParams.get('location') || '');
  const [seniority, setSeniority] = useState(searchParams.get('seniority') || '');
  const [employmentType, setEmploymentType] = useState(searchParams.get('employment_type') || '');
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10));
  const [results, setResults] = useState<SearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDictionary, setShowDictionary] = useState(false);
  const [dictTerm, setDictTerm] = useState('');
  const [dictKind, setDictKind] = useState<'skill' | 'role' | 'industry'>('skill');
  const [dictResult, setDictResult] = useState<DictionaryCheckResponse | null>(null);

  const performSearch = useCallback(async () => {
    setLoading(true);
    setError(null);

    const request: SearchRequest = {
      query: query.trim() || 'software engineer',
      location: location.trim() || undefined,
      seniority: seniority || undefined,
      employment_type: employmentType || undefined,
      page,
      per_page: 20,
    };

    // Update URL
    const params = new URLSearchParams();
    if (query.trim()) params.set('q', query.trim());
    if (location.trim()) params.set('location', location.trim());
    if (seniority) params.set('seniority', seniority);
    if (employmentType) params.set('employment_type', employmentType);
    if (page > 1) params.set('page', page.toString());
    setSearchParams(params, { replace: true });

    try {
      const data: SearchResponse = await api.search(request);
      setResults(data.results);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
      setTotal(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  }, [query, location, seniority, employmentType, page, setSearchParams]);

  useEffect(() => {
    performSearch();
  }, [performSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    performSearch();
  };

  const checkDictionary = async () => {
    if (!dictTerm.trim()) return;
    try {
      const result = await api.checkDictionary(dictTerm.trim(), dictKind);
      setDictResult(result);
    } catch (err) {
      setDictResult(null);
      console.error('Dictionary check failed:', err);
    }
  };

  const submitDictionary = async () => {
    if (!dictTerm.trim()) return;
    try {
      await api.submitDictionary(dictTerm.trim(), dictKind);
      alert('Term submitted for review!');
      setDictResult(null);
      setDictTerm('');
    } catch (err) {
      alert('Failed to submit term');
      console.error('Dictionary submit failed:', err);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-background)' }}>
      {/* Header */}
      <header style={{ background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)', position: 'sticky', top: 0, zIndex: 100 }}>
        <div className="container" style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            Nexus Hub
          </h1>
          <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              onClick={() => setShowDictionary(!showDictionary)}
              className="btn btn-outline"
              style={{ padding: '0.5rem 1rem' }}
            >
              Dictionary
            </button>
          </nav>
        </div>
      </header>

      {/* Search Form */}
      <section style={{ padding: '2rem 0' }}>
        <div className="container">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '800px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.75rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <label htmlFor="query" className="sr-only">Search query</label>
                <input
                  id="query"
                  type="search"
                  className="input"
                  placeholder="What are you looking for? (e.g., 'machine learning engineer', 'react typescript remote')"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  style={{ flex: 1, minWidth: 0 }}
                  autoComplete="off"
                />
                <label htmlFor="location" className="sr-only">Location</label>
                <input
                  id="location"
                  type="text"
                  className="input"
                  placeholder="Location (optional)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  style={{ width: '200px' }}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={loading} style={{ height: 'fit-content', minWidth: '120px' }}>
                {loading ? 'Searching…' : 'Search'}
              </button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
              <label htmlFor="seniority" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Seniority:</label>
              <select
                id="seniority"
                className="input"
                value={seniority}
                onChange={(e) => { setSeniority(e.target.value); setPage(1); }}
                style={{ width: 'auto', minWidth: '140px' }}
              >
                {SENIORITY_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt || 'Any'}</option>
                ))}
              </select>

              <label htmlFor="employment_type" style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Type:</label>
              <select
                id="employment_type"
                className="input"
                value={employmentType}
                onChange={(e) => { setEmploymentType(e.target.value); setPage(1); }}
                style={{ width: 'auto', minWidth: '160px' }}
              >
                {EMPLOYMENT_TYPES.map((opt) => (
                  <option key={opt} value={opt}>{opt || 'Any'}</option>
                ))}
              </select>
            </div>
          </form>
        </div>
      </section>

      {/* Dictionary Panel */}
      {showDictionary && (
        <section style={{ background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)', padding: '1.5rem 0' }}>
          <div className="container" style={{ maxWidth: '600px' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Dictionary Coverage Check</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}>
              Check if a skill, role, or industry is in our dictionaries. Misses are recorded for maintainer review.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'flex-end' }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label htmlFor="dict-term" className="sr-only">Term</label>
                <input
                  id="dict-term"
                  type="text"
                  className="input"
                  placeholder="Enter a skill, role, or industry (e.g., k8s, swe, fintech)"
                  value={dictTerm}
                  onChange={(e) => setDictTerm(e.target.value)}
                />
              </div>
              <select
                className="input"
                value={dictKind}
                onChange={(e) => setDictKind(e.target.value as 'skill' | 'role' | 'industry')}
                style={{ width: 'auto', minWidth: '140px' }}
              >
                <option value="skill">Skill</option>
                <option value="role">Role</option>
                <option value="industry">Industry</option>
              </select>
              <button onClick={checkDictionary} className="btn btn-primary" disabled={!dictTerm.trim()}>
                Check
              </button>
            </div>

            {dictResult && (
              <div style={{ marginTop: '1rem', padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--color-background)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <span className={`badge ${dictResult.type === 'canonical' ? 'badge-success' : dictResult.type === 'alias' ? 'badge-primary' : 'badge-warning'}`}>
                    {dictResult.type.charAt(0).toUpperCase() + dictResult.type.slice(1)}
                  </span>
                  <span style={{ fontWeight: 500 }}>"{dictResult.term}"</span>
                </div>
                {dictResult.type === 'canonical' && (
                  <p style={{ fontSize: '0.875rem' }}>
                    This is a canonical <strong>{dictResult.kind}</strong> entry: <strong>{dictResult.display}</strong>
                  </p>
                )}
                {dictResult.type === 'alias' && (
                  <p style={{ fontSize: '0.875rem' }}>
                    Resolves to canonical <strong>{dictResult.kind}</strong>: <strong>{dictResult.canonical}</strong>
                  </p>
                )}
                {dictResult.type === 'miss' && (
                  <>
                    <p style={{ fontSize: '0.875rem', marginBottom: '0.75rem' }}>
                      Not found in our <strong>{dictResult.kind}</strong> dictionary.
                    </p>
                    <button
                      onClick={submitDictionary}
                      className="btn btn-outline"
                      style={{ padding: '0.5rem 1rem' }}
                    >
                      Request Addition
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </section>
      )}

      {/* Results */}
      <main style={{ padding: '2rem 0' }}>
        <div className="container">
          {error && (
            <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: '#fef2f2', border: '1px solid #fecaca', color: 'var(--color-error)', marginBottom: '1.5rem' }}>
              {error}
            </div>
          )}

          {results.length === 0 && !loading && !error && (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-muted)' }}>
              <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>No jobs found</p>
              <p>Try adjusting your search terms or filters</p>
            </div>
          )}

          {results.length > 0 && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <p style={{ color: 'var(--color-text-muted)' }}>
                  {total} result{total !== 1 ? 's' : ''} for &ldquo;{query || 'software engineer'}&rdquo;
                  {location && ` in ${location}`}
                </p>
              </div>

              <div style={{ display: 'grid', gap: '1rem' }}>
                {results.map((result) => (
                  <JobCard key={result.job.id} result={result} />
                ))}
              </div>

              {totalPages > 1 && (
                <nav style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '2rem' }} aria-label="Pagination">
                  {page > 1 && (
                    <button
                      onClick={() => setPage(page - 1)}
                      className="btn btn-outline"
                      disabled={loading}
                    >
                      Previous
                    </button>
                  )}
                  <span style={{ display: 'flex', alignItems: 'center', padding: '0 1rem', color: 'var(--color-text-muted)' }}>
                    Page {page} of {totalPages}
                  </span>
                  {page < totalPages && (
                    <button
                      onClick={() => setPage(page + 1)}
                      className="btn btn-outline"
                      disabled={loading}
                    >
                      Next
                    </button>
                  )}
                </nav>
              )}
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer style={{ padding: '2rem 0', borderTop: '1px solid var(--color-border)', marginTop: 'auto' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          <p>Nexus Hub — AI-powered job search for developers</p>
          <p>{"Ryan Vo " + String.fromCharCode(60) + "ryandtvo@gmail.com" + String.fromCharCode(62)}</p>
        </div>
      </footer>
    </div>
  );
}