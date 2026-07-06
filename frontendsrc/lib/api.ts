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

export type ResearcherExternalProfile = {
  id: string;
  lattesId: string;
  nome: string;
  tipo?: string | null;
  formacaoAcademica?: string | null;
  openAlexId?: string | null;
  orcidId?: string | null;
  imageUrl?: string | null;
  indexH?: number | null;
  indexI10?: number | null;
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

export type UnifiedSearchResult = {
  result_type: "paper" | "conference_paper" | "advising" | "researcher";
  id: number;
  title: string;
  year?: number | null;
  researcher_id?: number | null;
  primary_researcher?: Pick<Researcher, "id" | "full_name"> | null;
  authors: Pick<Researcher, "id" | "full_name">[];
  areas: Array<{
    major_area?: string | null;
    area?: string | null;
    sub_area?: string | null;
    specialty?: string | null;
  }>;
  metadata: Record<string, string | number | boolean | null>;
  score: number;
};

export type AnalyticsSummary = {
  total_researchers: number;
  total_unique_publications: number;
  total_authorships: number;
  collaborative_publications: number;
  productions_by_type: Record<
    string,
    {
      unique_publications: number;
      authorships: number;
      collaborative_publications: number;
    }
  >;
  papers_without_doi: number;
  conference_papers_without_doi: number;
  duplicate_doi_groups: number;
  average_curriculum_update_year?: number | null;
};

export type AnalyticsYearRow = {
  year: number;
  type: "paper" | "conference_paper" | "advising";
  unique_publications: number;
  authorships: number;
  collaborative_publications: number;
};

export type AnalyticsAreaRow = {
  area: string;
  unique_publications: number;
  authorships: number;
  collaborative_publications: number;
};

export type AnalyticsResearcherRow = {
  researcher_id: number;
  full_name: string;
  unique_publications: number;
  authorships: number;
  collaborative_publications: number;
};

export type AnalyticsCoauthorNetwork = {
  nodes: Array<{ id: number; label: string }>;
  edges: Array<{ source: number; target: number; weight: number }>;
};

type RawSearchResult = {
  paper: Paper;
  score: number | string | null;
};

type QueryValue = string | number | boolean | null | undefined;

function apiBaseUrl() {
  const configured = (import.meta.env as { VITE_API_BASE_URL?: string })
    .VITE_API_BASE_URL;
  if (configured) return configured.replace(/\/$/, "");

  if (typeof window === "undefined") {
    return "http://localhost:5000";
  }

  // In browser, return empty string for relative paths
  // which will be proxied by our server.js.
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

async function apiFetch<T>(
  path: string,
  query?: Record<string, QueryValue>,
): Promise<T> {
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

export function getResearcherExternalProfile(id: string | number) {
  return apiFetch<{
    researcher: Researcher;
    external_profile: ResearcherExternalProfile | null;
  }>(`/researchers/${id}/external-profile`);
}

export function listPapers(query?: Record<string, QueryValue>) {
  return apiFetch<Paper[]>("/papers", query);
}

export function getPaper(id: string | number) {
  return apiFetch<Paper>(`/papers/${id}`);
}

export function listResearchAreas(query?: Record<string, QueryValue>) {
  return apiFetch<ResearchArea[]>("/research-areas", query);
}

export function listConferencePapers(query?: Record<string, QueryValue>) {
  return apiFetch<ConferencePaper[]>("/conference-papers", query);
}

export function getConferencePaper(id: string | number) {
  return apiFetch<ConferencePaper>(`/conference-papers/${id}`);
}

export function listAdvisings(query?: Record<string, QueryValue>) {
  return apiFetch<Advising[]>("/advisings", query);
}

export function getAdvising(id: string | number) {
  return apiFetch<Advising>(`/advisings/${id}`);
}

export async function searchPapers(query: string, limit = 10) {
  try {
    const results = await apiFetch<RawSearchResult[]>("/papers/search", {
      q: query,
      limit,
    });
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

export function searchAll(
  query: string,
  options?: {
    limit?: number;
    offset?: number;
    types?: string[];
    resultKinds?: string[];
    yearFrom?: string | number;
    yearTo?: string | number;
    area?: string;
    researcherId?: string | number;
  },
) {
  return apiFetch<UnifiedSearchResult[]>("/search", {
    q: query,
    limit: options?.limit ?? 10,
    offset: options?.offset,
    types:
      options?.types === undefined
        ? undefined
        : options.types.length > 0
          ? options.types.join(",")
          : "__none__",
    result_kinds:
      options?.resultKinds === undefined
        ? undefined
        : options.resultKinds.length > 0
          ? options.resultKinds.join(",")
          : "__none__",
    year_from: options?.yearFrom,
    year_to: options?.yearTo,
    area: options?.area,
    researcher_id: options?.researcherId,
  });
}

type AnalyticsOptions = {
  types?: string[];
  yearFrom?: string | number;
  yearTo?: string | number;
  area?: string;
  limit?: number;
};

function analyticsQuery(options?: AnalyticsOptions) {
  return {
    types:
      options?.types === undefined
        ? undefined
        : options.types.length > 0
          ? options.types.join(",")
          : "__none__",
    year_from: options?.yearFrom,
    year_to: options?.yearTo,
    area: options?.area,
    limit: options?.limit,
  };
}

export function getAnalyticsSummary(options?: AnalyticsOptions) {
  return apiFetch<AnalyticsSummary>(
    "/analytics/summary",
    analyticsQuery(options),
  );
}

export function getAnalyticsPublicationsByYear(options?: AnalyticsOptions) {
  return apiFetch<AnalyticsYearRow[]>(
    "/analytics/publications-by-year",
    analyticsQuery(options),
  );
}

export function getAnalyticsPublicationsByArea(options?: AnalyticsOptions) {
  return apiFetch<AnalyticsAreaRow[]>(
    "/analytics/publications-by-area",
    analyticsQuery(options),
  );
}

export function getAnalyticsTopResearchers(options?: AnalyticsOptions) {
  return apiFetch<AnalyticsResearcherRow[]>(
    "/analytics/top-researchers",
    analyticsQuery(options),
  );
}

export function getAnalyticsCoauthorNetwork(options?: AnalyticsOptions) {
  return apiFetch<AnalyticsCoauthorNetwork>(
    "/analytics/coauthor-network",
    analyticsQuery(options),
  );
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export async function downloadAnalyticsCSV(
  type: "researchers" | "areas" | "report",
  options?: AnalyticsOptions,
) {
  const query = analyticsQuery(options);
  const params = new URLSearchParams();
  params.set("type", type);
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") continue;
    params.set(key, String(value));
  }
  const url = `${apiBaseUrl()}/analytics/export/csv?${params.toString()}`;
  const response = await fetch(url, {
    headers: { Accept: "text/csv" },
  });
  if (!response.ok) {
    throw new Error(`Export CSV ${response.status}: ${await response.text()}`);
  }
  const blob = await response.blob();
  const filename_map: Record<string, string> = {
    researchers: "pesquisadores.csv",
    areas: "areas.csv",
    report: "relatorio-analitico.csv",
  };
  triggerDownload(blob, filename_map[type] ?? `${type}.csv`);
}
