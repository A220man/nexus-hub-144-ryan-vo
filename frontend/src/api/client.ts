// API Types
export interface Job {
  id: number;
  external_id: string;
  title: string;
  company: string;
  location: string | null;
  description: string;
  url: string;
  source: string;
  posted_at: string | null;
  fetched_at: string | null;
  skills: string[];
  seniority: string | null;
  employment_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string | null;
}

export interface SearchResult {
  job: Job;
  match_score: number;
  match_explanation: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface SearchRequest {
  query: string;
  location?: string;
  skills?: string[];
  seniority?: string;
  employment_type?: string;
  page: number;
  per_page: number;
}

export interface DictionaryCheckResponse {
  type: 'canonical' | 'alias' | 'miss';
  canonical: string | null;
  display: string | null;
  term: string;
  kind: string;
}

export interface DictionarySubmitRequest {
  term: string;
  kind: string;
}

export interface DictionarySubmitResponse {
  status: 'created' | 'updated';
  id: number;
  request_count: number;
}

export interface DictionaryPendingItem {
  id: number;
  kind: string;
  raw_term: string;
  normalized_term: string;
  request_count: number;
  first_requested_at: string;
  last_requested_at: string;
  submitted_by: string | null;
  status: string;
  resolution_note: string | null;
}

const API_BASE = '/api';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  search: (request: SearchRequest) =>
    fetchJson<SearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  checkDictionary: (term: string, kind: string) =>
    fetchJson<DictionaryCheckResponse>('/dictionary/check', {
      method: 'POST',
      body: JSON.stringify({ term, kind }),
    }),

  submitDictionary: (term: string, kind: string) =>
    fetchJson<DictionarySubmitResponse>('/dictionary/submit', {
      method: 'POST',
      body: JSON.stringify({ term, kind }),
    }),

  getPendingDictionary: (kind?: string, status = 'pending', limit = 100) => {
    const params = new URLSearchParams();
    if (kind) params.set('kind', kind);
    params.set('status', status);
    params.set('limit', limit.toString());
    return fetchJson<DictionaryPendingItem[]>(`/dictionary/pending?${params.toString()}`);
  },

  health: () => fetchJson<{ status: string; version: string }>('/health'),
};