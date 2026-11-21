import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useLocation, useNavigate } from 'react-router-dom';
import { api, DictionaryCheckResponse } from '../api/client';

export function DictionaryPage() {
  const [term, setTerm] = useState('');
  const [kind, setKind] = useState<'skill' | 'role' | 'industry'>('skill');
  const [result, setResult] = useState<DictionaryCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSubmit, setShowSubmit] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Pre-fill from URL query params if present
    const params = new URLSearchParams(location.search);
    const termFromUrl = params.get('t') || '';
    const kindFromUrl = params.get('k') || 'skill';
    if (termFromUrl) {
      setTerm(termFromUrl);
      setKind(kindFromUrl as 'skill' | 'role' | 'industry');
    }
  }, [location.search]);

  const check = useCallback(async () => {
    if (!term.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await api.checkDictionary(term.trim(), kind);
      setResult(data);
    } catch (err) {
      console.error('Dictionary check failed:', err);
    } finally {
      setLoading(false);
    }
  }, [term, kind]);

  const submit = useCallback(async () => {
    if (!term.trim()) return;
    try {
      await api.submitDictionary(term.trim(), kind);
      setShowSubmit(true);
      setTimeout(() => setShowSubmit(false), 3000);
      setTerm('');
      setResult(null);
    } catch (err) {
      console.error('Dictionary submit failed:', err);
    }
  }, [term, kind]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      check();
    }
  }, [check]);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-background)' }}>
      <header style={{
        background: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        padding: '1rem 1.5rem',
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            Dictionary Coverage
          </h1>
          <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              onClick={() => navigate('/')}
              className="btn btn-outline"
              style={{ padding: '0.5rem 1rem' }}
            >
              Back to Jobs
            </button>
          </nav>
        </div>
      </header>

      <main style={{ padding: '2rem 1.5rem' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>
            Check Dictionary Coverage
          </h2>

          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '1.5rem' }}>
            Enter a skill, role, or industry to check if it exists in our canonical dictionaries.
            Unknown terms are recorded for maintainer review with deduplication.
          </p>

          <form
            style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
            onSubmit={(e) => { e.preventDefault(); check(); }}
          >
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <label htmlFor="dict-term" className="sr-only">Term</label>
              <input
                id="dict-term"
                type="text"
                className="input"
                placeholder="Enter a skill, role, or industry (e.g., k8s, swe, fintech)"
                value={term}
                onChange={(e) => setTerm(e.target.value)}
                onKeyDown={handleKeyDown}
                autoComplete="off"
              />
              <select
                className="input"
                value={kind}
                onChange={(e) => setKind(e.target.value as 'skill' | 'role' | 'industry')}
                style={{ width: 'auto', minWidth: '140px' }}
              >
                <option value="skill">Skill</option>
                <option value="role">Role</option>
                <option value="industry">Industry</option>
              </select>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!term.trim() || loading}
                style={{ height: 'fit-content', minWidth: '100px' }}
              >
                {loading ? 'Checking…' : 'Check'}
              </button>
            </div>
          </form>

          {result && (
            <div style={{ marginTop: '1.5rem', padding: '1.5rem', borderRadius: 'var(--radius-md)', background: 'var(--color-background)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <span className={`badge ${result.type === 'canonical' ? 'badge-success' : result.type === 'alias' ? 'badge-primary' : 'badge-warning'}`}>
                  {result.type.charAt(0).toUpperCase() + result.type.slice(1)}
                </span>
                <span style={{ fontWeight: 500 }}>{`"{result.term}"`}
                </span>
              </div>

              {result.type === 'canonical' && (
                <p style={{ fontSize: '0.875rem' }}>
                  This is a canonical <strong>{result.kind}</strong> entry:
                  <strong>{result.display}</strong>
                </p>
              )}

              {result.type === 'alias' && (
                <p style={{ fontSize: '0.875rem' }}>
                  Resolves to canonical <strong>{result.kind}</strong>:
                  <strong>{result.canonical}</strong>
                </p>
              )}

              {result.type === 'miss' && (
                <>
                  <p style={{ fontSize: '0.875rem', marginBottom: '0.75rem' }}>
                    Not found in our <strong>{result.kind}</strong> dictionary.
                  </p>
                  <button
                    onClick={submit}
                    className="btn btn-outline"
                    style={{ padding: '0.5rem 1rem' }}
                  >
                    Request Addition
                  </button>
                </>
              )}
            </div>
          )}

          {showSubmit && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', borderRadius: 'var(--radius-md)', background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-green)' }}>
                Term submitted for review! Thank you for helping improve our dictionaries.
              </p>
            </div>
          )}
        </div>
      </main>

      <footer style={{ padding: '2rem 1.5rem', borderTop: '1px solid var(--color-border)', marginTop: 'auto', textAlign: 'center', color: 'var(--color-text-muted)' }}>
        <p>Nexus Hub — Dictionary Coverage Checker</p>
      </footer>
    </div>
  );
}
