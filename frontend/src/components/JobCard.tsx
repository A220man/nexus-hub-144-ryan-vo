import { SearchResult } from '../api/client';

interface JobCardProps {
  result: SearchResult;
}

export function JobCard({ result }: JobCardProps) {
  const { job, match_score, match_explanation } = result;
  const scorePercent = Math.round(match_score * 100);
  const scoreClass = match_score >= 0.7 ? 'high' : match_score >= 0.4 ? 'medium' : 'low';

  const formatSalary = (min: number | null, max: number | null, currency: string | null) => {
    if (!min && !max) return null;
    const c = currency || 'USD';
    if (min && max) return `${c} ${min.toLocaleString()}–${max.toLocaleString()}`;
    if (min) return `${c} ${min.toLocaleString()}+`;
    return `Up to ${c} ${max!.toLocaleString()}`;
  };

  return (
    <article className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.25rem' }}>
            <a href={job.url} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit' }}>
              {job.title}
            </a>
          </h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
            {job.company} • {job.location || 'Remote'}
          </p>
        </div>
        <div className={`match-score ${scoreClass}`} style={{ fontSize: '1.5rem', whiteSpace: 'nowrap' }}>
          {scorePercent}%
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {job.skills.slice(0, 6).map((skill) => (
          <span key={skill} className="badge badge-primary">{skill}</span>
        ))}
        {job.skills.length > 6 && (
          <span className="badge badge-muted">+{job.skills.length - 6} more</span>
        )}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
        {job.seniority && (
          <span className="badge badge-muted">{job.seniority}</span>
        )}
        {job.employment_type && (
          <span className="badge badge-muted">{job.employment_type.replace('-', ' ')}</span>
        )}
        {formatSalary(job.salary_min, job.salary_max, job.currency) && (
          <span className="badge badge-success">{formatSalary(job.salary_min, job.salary_max, job.currency)}</span>
        )}
      </div>

      <details style={{ borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 500, color: 'var(--color-text-muted)' }}>
          Why this match?
        </summary>
        <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', lineHeight: 1.6 }}>
          {match_explanation}
        </p>
      </details>

      <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto' }}>
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
          style={{ flex: 1 }}
        >
          View Job
        </a>
      </div>
    </article>
  );
}