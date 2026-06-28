import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Check, FileText, Search, SlidersHorizontal, User } from "lucide-react";
import {
  listAdvisings,
  listConferencePapers,
  listPapers,
  listResearchAreas,
  listResearchers,
  searchPapers,
  type Advising,
  type ConferencePaper,
  type Paper,
  type ResearchArea,
  type Researcher,
  type SearchResult,
} from "@/lib/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Portal de Pesquisa Lattes" },
      { name: "description", content: "Busca de pesquisadores e producoes cientificas." },
    ],
  }),
  component: Home,
});

const PUBLICATION_TYPES = ["Paper", "Conference Paper", "Advising"] as const;
type PublicationType = (typeof PUBLICATION_TYPES)[number];

const RESULT_KINDS = ["Pesquisadores", "Publicacoes"] as const;
type ResultKind = (typeof RESULT_KINDS)[number];

function normalize(value: string | null | undefined) {
  return (value ?? "").toLowerCase();
}

function uniqueAreas(areas: ResearchArea[]) {
  return Array.from(
    new Set(
      areas
        .flatMap((area) => [area.major_area, area.area, area.sub_area, area.specialty])
        .filter((value): value is string => Boolean(value)),
    ),
  );
}

function Home() {
  const [query, setQuery] = useState("");
  const [committedQuery, setCommittedQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [researchers, setResearchers] = useState<Researcher[]>([]);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [conferencePapers, setConferencePapers] = useState<ConferencePaper[]>([]);
  const [advisings, setAdvisings] = useState<Advising[]>([]);
  const [areas, setAreas] = useState<ResearchArea[]>([]);
  const [paperResults, setPaperResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const hasQuery = committedQuery.trim().length > 0;


  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [typeFilters, setTypeFilters] = useState<Record<PublicationType, boolean>>({
    Paper: true,
    "Conference Paper": true,
    Advising: true,
  });
  const [resultKinds, setResultKinds] = useState<Record<ResultKind, boolean>>({
    Pesquisadores: true,
    Publicacoes: true,
  });
  const [filtersApplied, setFiltersApplied] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadInitialData() {
      try {
        setLoading(true);
        const [researcherData, paperData, areaData, conferenceData, advisingData] = await Promise.all([
          listResearchers(),
          listPapers(),
          listResearchAreas(),
          listConferencePapers(),
          listAdvisings(),
        ]);

        if (!active) return;
        setResearchers(researcherData);
        setPapers(paperData);
        setAreas(areaData);
        setConferencePapers(conferenceData);
        setAdvisings(advisingData);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Nao foi possivel carregar os dados.");
      } finally {
        if (active) setLoading(false);
      }
    }

    loadInitialData();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function runPaperSearch() {
      if (!hasQuery) {
        setPaperResults([]);
        return;
      }

      try {
        setSearching(true);
        const results = await searchPapers(committedQuery, 8);
        if (active) setPaperResults(results);
      } catch (err) {
        if (active) {
          setPaperResults([]);
          setError(err instanceof Error ? err.message : "Erro ao buscar publicacoes.");
        }
      } finally {
        if (active) setSearching(false);
      }
    }

    runPaperSearch();
    return () => {
      active = false;
    };
  }, [committedQuery, hasQuery]);

  const papersByResearcher = useMemo(() => {
    const counts = new Map<number, number>();
    for (const paper of papers) {
      counts.set(paper.researcher_id, (counts.get(paper.researcher_id) ?? 0) + 1);
    }
    return counts;
  }, [papers]);

  const areasByResearcher = useMemo(() => {
    const grouped = new Map<number, ResearchArea[]>();
    for (const area of areas) {
      const current = grouped.get(area.researcher_id) ?? [];
      current.push(area);
      grouped.set(area.researcher_id, current);
    }
    return grouped;
  }, [areas]);

 
  const isWithinYearRange = useMemo(() => {
    const fromYear = yearFrom.trim() ? Number(yearFrom) : null;
    const toYear = yearTo.trim() ? Number(yearTo) : null;
    return (year: number | null | undefined) => {
      if (year == null) return true;
      if (fromYear != null && year < fromYear) return false;
      if (toYear != null && year > toYear) return false;
      return true;
    };
  }, [yearFrom, yearTo]);

  const eligibleResearcherIds = useMemo(() => {
    const ids = new Set<number>();

    if (typeFilters.Paper) {
      for (const paper of papers) {
        if (isWithinYearRange(paper.year)) ids.add(paper.researcher_id);
      }
    }

    if (typeFilters["Conference Paper"]) {
      for (const conferencePaper of conferencePapers) {
        if (isWithinYearRange(conferencePaper.year)) ids.add(conferencePaper.researcher_id);
      }
    }

    if (typeFilters.Advising) {
      for (const advising of advisings) {
        ids.add(advising.researcher_id);
      }
    }

    return ids;
  }, [papers, conferencePapers, advisings, typeFilters, isWithinYearRange]);

  const researcherResults = useMemo(() => {
    if (!hasQuery) return [];
    const lowered = normalize(committedQuery);

    return researchers.filter((researcher) => {
      if (!eligibleResearcherIds.has(researcher.id)) return false;

      const researcherAreas = uniqueAreas(areasByResearcher.get(researcher.id) ?? []);
      return (
        normalize(researcher.full_name).includes(lowered) ||
        normalize(researcher.citation_name).includes(lowered) ||
        normalize(researcher.lattes_id).includes(lowered) ||
        researcherAreas.some((area) => normalize(area).includes(lowered))
      );
    });
  }, [areasByResearcher, committedQuery, eligibleResearcherIds, hasQuery, researchers]);


  const filteredPaperResults = useMemo(() => {
    if (!typeFilters.Paper) return [];
    return paperResults.filter(({ paper }) => isWithinYearRange(paper.year));
  }, [paperResults, typeFilters, isWithinYearRange]);

  const showResearchers = resultKinds.Pesquisadores;
  const showPublications = resultKinds.Publicacoes;

  const visibleResearcherResults = showResearchers ? researcherResults : [];
  const visiblePaperResults = showPublications ? filteredPaperResults : [];

  const handleSearch = () => {
    setCommittedQuery(query.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const toggleType = (type: PublicationType) => {
    setTypeFilters((current) => ({ ...current, [type]: !current[type] }));
  };

  const toggleResultKind = (kind: ResultKind) => {
    setResultKinds((current) => ({ ...current, [kind]: !current[kind] }));
  };

  const handleApplyFilters = () => {
    setFiltersApplied(true);
    setTimeout(() => setFiltersApplied(false), 1500);
  };

  const totalResults = visibleResearcherResults.length + visiblePaperResults.length;

  const filtersPanel = (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-xs font-medium text-muted-foreground">
            Intervalo de Anos
          </label>
          <div className="flex gap-2">
            <input
              value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)}
              placeholder="De"
              inputMode="numeric"
              className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
            />
            <input
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              placeholder="Ate"
              inputMode="numeric"
              className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
            />
          </div>
        </div>
        <div>
          <label className="mb-2 block text-xs font-medium text-muted-foreground">
            Tipo de Publicacao
          </label>
          <div className="grid grid-cols-1 gap-1.5 text-sm">
            {PUBLICATION_TYPES.map((type) => (
              <label key={type} className="flex items-center gap-2 text-foreground/90">
                <input
                  type="checkbox"
                  checked={typeFilters[type]}
                  onChange={() => toggleType(type)}
                  className="h-3.5 w-3.5 accent-[var(--teal)]"
                />
                {type}
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="mb-2 block text-xs font-medium text-muted-foreground">
            Mostrar resultados de
          </label>
          <div className="grid grid-cols-1 gap-1.5 text-sm">
            {RESULT_KINDS.map((kind) => (
              <label key={kind} className="flex items-center gap-2 text-foreground/90">
                <input
                  type="checkbox"
                  checked={resultKinds[kind]}
                  onChange={() => toggleResultKind(kind)}
                  className="h-3.5 w-3.5 accent-[var(--teal)]"
                />
                {kind}
              </label>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleApplyFilters}
          className={`flex items-center gap-1.5 rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
            filtersApplied
              ? "bg-[var(--teal)] text-primary-foreground"
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          }`}
        >
          {filtersApplied ? (
            <>
              <Check className="h-4 w-4" />
              Aplicado
            </>
          ) : (
            "Aplicar"
          )}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background ml-[200px]">
      <header className="border-b border-border bg-sidebar/60 px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6">
          <Link to="/" className="font-serif text-xl text-foreground">
            Portal de Pesquisa <span className="text-primary">Lattes</span>
          </Link>
          {hasQuery && (
            <div className="flex flex-1 items-center gap-2">
              <div className="relative flex-1">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Buscar pesquisador, area ou publicacao"
                  className="w-full rounded-full border border-border bg-input py-2 pl-4 pr-10 text-sm text-foreground focus:border-primary focus:outline-none"
                />
                <button
                  onClick={handleSearch}
                  aria-label="Buscar"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary"
                >
                  <Search className="h-4 w-4" />
                </button>
              </div>
              <button
                onClick={() => setShowFilters((value) => !value)}
                aria-label="Filtros"
                className={`shrink-0 rounded-full bg-primary p-2 text-primary-foreground transition-colors hover:bg-primary/90 ${
                  showFilters ? "ring-2 ring-[var(--teal)] ring-offset-2 ring-offset-background" : ""
                }`}
              >
                <SlidersHorizontal className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </header>

      {hasQuery && showFilters && (
        <div className="border-b border-border bg-sidebar/60 px-6 py-5">
          <div className="mx-auto max-w-6xl">{filtersPanel}</div>
        </div>
      )}

      {!hasQuery ? (
        <section className="flex min-h-[calc(100vh-72px)] flex-col items-center justify-center px-6">
          <h1 className="mb-10 text-center font-serif text-5xl tracking-tight text-foreground">
            Portal de Pesquisa <span className="text-primary">Lattes</span>
          </h1>
          <div className="flex w-full max-w-2xl items-center gap-2">
            <div className="relative flex-1">
              <input
                autoFocus
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Buscar pesquisador, area ou publicacao..."
                className="w-full rounded-full border border-border bg-input py-3 pl-5 pr-12 text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
              />
              <button
                onClick={handleSearch}
                aria-label="Buscar"
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-muted-foreground hover:text-primary"
              >
                <Search className="h-5 w-5" />
              </button>
            </div>
            <button
              onClick={() => setShowFilters((value) => !value)}
              className={`rounded-full bg-primary p-3 text-primary-foreground transition-colors hover:bg-primary/90 ${
                showFilters ? "ring-2 ring-[var(--teal)] ring-offset-2 ring-offset-background" : ""
              }`}
            >
              <SlidersHorizontal className="h-5 w-5" />
            </button>
          </div>

          {showFilters && <div className="mt-6 w-full max-w-2xl">{filtersPanel}</div>}

          {loading && <p className="mt-6 text-sm text-muted-foreground">Carregando dados do banco...</p>}
          {error && <p className="mt-6 max-w-xl text-center text-sm text-destructive">{error}</p>}
        </section>
      ) : (
        <section className="mx-auto max-w-6xl px-6 py-8">
          <p className="mb-4 text-sm text-muted-foreground">
            {searching ? "Buscando..." : `${totalResults} resultado${totalResults !== 1 ? "s" : ""} encontrado${totalResults !== 1 ? "s" : ""}`}
          </p>
          {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

          {visibleResearcherResults.length > 0 && (
            <>
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Pesquisadores
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {visibleResearcherResults.map((researcher) => {
                  const researcherAreas = uniqueAreas(areasByResearcher.get(researcher.id) ?? []);
                  return (
                    <button
                      key={researcher.id}
                      onClick={() =>
                        navigate({ to: "/pesquisador/$id", params: { id: String(researcher.id) } })
                      }
                      className="group flex items-start gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary hover:shadow-[0_0_0_1px_var(--teal)]"
                    >
                      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
                        <User className="h-7 w-7 text-primary" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-foreground group-hover:text-primary">
                          {researcher.full_name}
                        </h3>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                          ID Lattes: {researcher.lattes_id}
                        </p>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {researcherAreas.slice(0, 3).map((area) => (
                            <span
                              key={area}
                              className="rounded-full bg-primary/15 px-2 py-0.5 text-[11px] text-primary"
                            >
                              {area}
                            </span>
                          ))}
                        </div>
                        <p className="mt-3 text-xs font-medium text-foreground">
                          {papersByResearcher.get(researcher.id) ?? 0} publicacoes
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {visiblePaperResults.length > 0 && (
            <div className="mt-8">
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Publicacoes
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {visiblePaperResults.map(({ paper, score }) => (
                  <button
                    key={paper.id}
                    onClick={() =>
                      navigate({ to: "/publicacao/paper/$id", params: { id: String(paper.id) } })
                    }
                    className="group flex items-start gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary hover:shadow-[0_0_0_1px_var(--teal)]"
                  >
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-foreground group-hover:text-primary">
                        {paper.title}
                      </h3>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {paper.year ?? "Ano nao informado"} - score {score.toFixed(4)}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {!loading && !searching && totalResults === 0 && (
            <div className="rounded-xl border border-border bg-card p-8 text-center text-sm text-muted-foreground">
              Nenhum resultado encontrado para a busca.
            </div>
          )}
        </section>
      )}

      <footer className="border-t border-border px-6 py-4 text-xs text-muted-foreground">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <span>2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">
            Termos de uso
          </a>
        </div>
      </footer>
    </div>
  );
}