import { render, screen } from '@testing-library/react';
import { JobCard } from '../JobCard';
import { SearchResult } from '../../api/client';

const mockResult: SearchResult = {
  job: {
    id: 1,
    external_id: 'test-1',
    title: 'Senior ML Engineer',
    company: 'TestCorp',
    location: 'San Francisco, CA',
    description: 'Build ML systems',
    url: 'https://example.com/job/1',
    source: 'company',
    posted_at: '2024-01-15T00:00:00',
    fetched_at: '2024-01-15T00:00:00',
    skills: ['python', 'pytorch', 'machine learning', 'transformers'],
    seniority: 'senior',
    employment_type: 'full-time',
    salary_min: 200000,
    salary_max: 300000,
    currency: 'USD',
  },
  match_score: 0.85,
  match_explanation: 'This job has a strong semantic match (85%) to your search.',
};

describe('JobCard', () => {
  it('renders job title and company', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText('Senior ML Engineer')).toBeInTheDocument();
    expect(screen.getByText(/TestCorp/)).toBeInTheDocument();
  });

  it('renders location', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText(/San Francisco, CA/)).toBeInTheDocument();
  });

  it('renders match score with correct class', () => {
    render(<JobCard result={mockResult} />);
    const score = screen.getByText('85%');
    expect(score).toHaveClass('high');
  });

  it('renders skills as badges', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('pytorch')).toBeInTheDocument();
    expect(screen.getByText('machine learning')).toBeInTheDocument();
    expect(screen.getByText('transformers')).toBeInTheDocument();
  });

  it('renders salary range', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText('USD 200,000–300,000')).toBeInTheDocument();
  });

  it('renders seniority and employment type badges', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText('senior')).toBeInTheDocument();
    expect(screen.getByText('full time')).toBeInTheDocument();
  });

  it('renders match explanation in details', () => {
    render(<JobCard result={mockResult} />);
    expect(screen.getByText('Why this match?')).toBeInTheDocument();
    // Details content is hidden until opened
    expect(screen.queryByText('strong semantic match')).not.toBeInTheDocument();
  });

  it('renders view job link', () => {
    render(<JobCard result={mockResult} />);
    const link = screen.getByRole('link', { name: 'View Job' });
    expect(link).toHaveAttribute('href', 'https://example.com/job/1');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('handles missing optional fields', () => {
    const minimalResult: SearchResult = {
      job: {
        ...mockResult.job,
        location: null,
        seniority: null,
        employment_type: null,
        salary_min: null,
        salary_max: null,
        currency: null,
        skills: [],
      },
      match_score: 0.3,
      match_explanation: 'Minimal match',
    };
    render(<JobCard result={minimalResult} />);
    expect(screen.getByText(/Remote/)).toBeInTheDocument();
    expect(screen.getByText('30%')).toHaveClass('low');
    expect(screen.queryByText('senior')).not.toBeInTheDocument();
  });
});