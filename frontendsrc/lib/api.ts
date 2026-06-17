export type Researcher = {
  id: number;
  full_name: string;
  lattes_id: string;
  citation_name?: string | null;
  orcid?: string | null;
  nationality?: string | null;
  birth_country?: string | null;
  birth_state?: string | null;
  update_date?: string | null;
};

export type Paper = {
  id: number;
  title: string;
  researcher_id: number;
  year?: number | null;
  doi?: string | null;
  language?: string | null;
  nature?: string | null;
  country?: string | null;
  journal?: string | null;
  issn?: string | null;
  volume?: string | null;
  issue?: string | null;
  first_page?: string | null;
  last_page?: string | null;
  title_embeddings?: number[] | null;
};

export type ResearchArea = {
  id: number;
  researcher_id: number;
  major_area?: string | null;
  area?: string | null;
  sub_area?: string | null;
  specialty?: string | null;
};

export type ConferencePaper = {
  id: number;
  researcher_id: number;
  title: string;
  year?: number | null;
  nature?: string | null;
  country?: string | null;
  language?: string | null;
  doi?: string | null;
  event_name?: string | null;
  event_city?: string | null;
  event_year?: number | null;
  event_classification?: string | null;
  proceedings_title?: string | null;
  isbn?: string | null;
  first_page?: string | null;
  last_page?: string | null;
};

export type Advising = {
  id: number;
  researcher_id: number;
  level: string;
  title: string;
  year?: number | null;
  advisee_name?: string | null;
  advising_type?: string | null;
  institution?: string | null;
  course?: string | null;
  country?: string | null;
  had_scholarship?: boolean | null;
  funding_agency?: string | null;
};

export type SearchResult = {
  paper: Paper;
  score: number;
};

type RawSearchResult = {
  paper: Paper;
  score: number | string | null;
};

type QueryValue = string | number | boolean | null | undefined;

function apiBaseUrl() {
  const configured = (import.meta.env as { VITE_API_BASE_URL?: string }).VITE_API_BASE_URL;
  if (configured) return configured.replace(/\/$/, "");

  if (typeof window === "undefined") {
    return "http://localhost:5000";
  }

  if (window.location.port && window.location.port !== "5000") {
    return "http://localhost:5000";
  }

  return "";
}

function pathWithQuery(path: string, query?: Record<string, QueryValue>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value === undefined || value === null || value === "") continue;
    params.set(key, String(value));
  }
  const qs = params.toString();
  return `${apiBaseUrl()}${path}${qs ? `?${qs}` : ""}`;
}

async function apiFetch<T>(path: string, query?: Record<string, QueryValue>): Promise<T> {
  const response = await fetch(pathWithQuery(path, query), {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API ${response.status}: ${await response.text()}`);
  }

  return response.json() as Promise<T>;
}

export function listResearchers(query?: Record<string, QueryValue>) {
  return apiFetch<Researcher[]>("/researchers", query);
}

export function getResearcher(id: string | number) {
  return apiFetch<Researcher>(`/researchers/${id}`);
}

export function listPapers(query?: Record<string, QueryValue>) {
  return apiFetch<Paper[]>("/papers", query);
}

export function listResearchAreas(query?: Record<string, QueryValue>) {
  return apiFetch<ResearchArea[]>("/research-areas", query);
}

export function listConferencePapers(query?: Record<string, QueryValue>) {
  return apiFetch<ConferencePaper[]>("/conference-papers", query);
}

export function listAdvisings(query?: Record<string, QueryValue>) {
  return apiFetch<Advising[]>("/advisings", query);
}

export async function searchPapers(query: string, limit = 10) {
  try {
    const results = await apiFetch<RawSearchResult[]>("/papers/search", { q: query, limit });
    return results.map(({ paper, score }) => ({
      paper,
      score: typeof score === "number" ? score : Number(score ?? 0),
    }));
  } catch {
    const papers = await listPapers();
    const lowered = query.toLowerCase();
    return papers
      .filter((paper) => paper.title.toLowerCase().includes(lowered))
      .slice(0, limit)
      .map((paper, index) => ({ paper, score: 1 / (index + 1) }));
  }
}
