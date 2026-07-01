import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Check, ChevronLeft, ChevronRight, FileText, GraduationCap, Presentation, Search, SlidersHorizontal, User } from "lucide-react";
import {
  getResearcherExternalProfile,
  listPapers,
  listResearchAreas,
  searchAll,
  type Paper,
  type ResearchArea,
  type UnifiedSearchResult,
} from "@/lib/api";

export const Route = createFileRoute("/")({
  validateSearch: (search: Record<string, unknown>) => ({
    q: typeof search.q === "string" ? search.q : undefined,
  }),
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

const PUBLICATION_TYPE_LABELS: Record<PublicationType, string> = {
  Paper: "Artigo de periodico",
  "Conference Paper": "Trabalho em evento",
  Advising: "Orientacao",
};

const RESULT_KIND_LABELS: Record<ResultKind, string> = {
  Pesquisadores: "Pesquisadores",
  Publicacoes: "Publicacoes",
};

const SEARCH_PAGE_SIZE = 10;

function uniqueAreas(areas: ResearchArea[]) {
  return Array.from(
    new Set(
      areas
        .flatMap((area) => [area.major_area, area.area, area.sub_area, area.specialty])
        .filter((value): value is string => Boolean(value)),
    ),
  );
}

function resultTypeLabel(type: UnifiedSearchResult["result_type"]) {
  if (type === "paper") return "Artigo de periodico";
  if (type === "conference_paper") return "Trabalho em evento";
  if (type === "advising") return "Orientacao";
  return "Pesquisador";
}

function resultSecondary(result: UnifiedSearchResult) {
  if (result.result_type === "paper") {
    return result.metadata.journal ?? result.metadata.doi ?? "";
  }
  if (result.result_type === "conference_paper") {
    return result.metadata.event_name ?? result.metadata.doi ?? "";
  }
  if (result.result_type === "advising") {
    return result.metadata.advisee_name ?? result.metadata.level ?? "";
  }
  return result.primary_researcher?.full_name ?? "";
}

function Home() {
  const { q: urlQuery = "" } = Route.useSearch();
  const [query, setQuery] = useState(urlQuery);
  const [committedQuery, setCommittedQuery] = useState(urlQuery);
  const [showFilters, setShowFilters] = useState(false);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [areas, setAreas] = useState<ResearchArea[]>([]);
  const [searchResults, setSearchResults] = useState<UnifiedSearchResult[]>([]);
  const [researcherImageUrls, setResearcherImageUrls] = useState<Record<number, string | null>>({});
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [hasMoreResults, setHasMoreResults] = useState(false);
  const [searchPage, setSearchPage] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const hasQuery = committedQuery.trim().length > 0;

  const [yearFrom, setYearFrom] = useState("1990");
  const [yearTo, setYearTo] = useState("2020");
  const [selectedArea, setSelectedArea] = useState("");
  const [typeFilters, setTypeFilters] = useState<Record<PublicationType, boolean>>({
    Paper: true,
    "Conference Paper": true,
    Advising: true,
  });
  const [resultKinds, setResultKinds] = useState<Record<ResultKind, boolean>>({
    Pesquisadores: false,
    Publicacoes: true,
  });
  const [filtersApplied, setFiltersApplied] = useState(false);

  const selectedSearchTypes = useMemo(() => {
    return PUBLICATION_TYPES
      .filter((type) => typeFilters[type])
      .map((type) => {
        if (type === "Conference Paper") return "conference_paper";
        return type.toLowerCase();
      });
  }, [typeFilters]);

  const selectedSearchResultKinds = useMemo(() => {
    return RESULT_KINDS
      .filter((kind) => resultKinds[kind])
      .map((kind) => (kind === "Pesquisadores" ? "researchers" : "publications"));
  }, [resultKinds]);

  useEffect(() => {
    let active = true;

    async function loadInitialData() {
      try {
        setLoading(true);
        const [paperData, areaData] = await Promise.all([
          listPapers(),
          listResearchAreas(),
        ]);

        if (!active) return;
        setPapers(paperData);
        setAreas(areaData);
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
    if (!hasQuery) return;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [hasQuery, searchPage]);

  useEffect(() => {
    setSearchPage(0);
  }, [
    committedQuery,
    selectedArea,
    selectedSearchResultKinds,
    selectedSearchTypes,
    yearFrom,
    yearTo,
  ]);

  useEffect(() => {
    let active = true;

    async function runSearch() {
      if (!hasQuery) {
        setSearchResults([]);
        setHasMoreResults(false);
        return;
      }

      try {
        setSearching(true);
        const results = await searchAll(committedQuery, {
          limit: SEARCH_PAGE_SIZE,
          offset: searchPage * SEARCH_PAGE_SIZE,
          types: selectedSearchTypes,
          resultKinds: selectedSearchResultKinds,
          yearFrom,
          yearTo,
          area: selectedArea,
        });
        if (active) {
          setSearchResults(results);
          setHasMoreResults(results.length === SEARCH_PAGE_SIZE);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setSearchResults([]);
          setHasMoreResults(false);
          setError(err instanceof Error ? err.message : "Erro ao buscar publicacoes.");
        }
      } finally {
        if (active) setSearching(false);
      }
    }

    runSearch();
    return () => {
      active = false;
    };
  }, [
    committedQuery,
    hasQuery,
    searchPage,
    selectedArea,
    selectedSearchResultKinds,
    selectedSearchTypes,
    yearFrom,
    yearTo,
  ]);

  const papersByResearcher = useMemo(() => {
    const counts = new Map<number, number>();
    for (const paper of papers) {
      counts.set(paper.researcher_id, (counts.get(paper.researcher_id) ?? 0) + 1);
    }
    return counts;
  }, [papers]);

  const areaOptions = useMemo(() => {
    return uniqueAreas(areas).sort((a, b) => a.localeCompare(b));
  }, [areas]);

  const showResearchers = resultKinds.Pesquisadores;
  const showPublications = resultKinds.Publicacoes;

  const visibleResearcherResults = showResearchers
    ? searchResults.filter((result) => result.result_type === "researcher")
    : [];
  const visiblePublicationResults = showPublications
    ? searchResults.filter((result) =>
        ["paper", "conference_paper", "advising"].includes(result.result_type),
      )
    : [];

  useEffect(() => {
    let active = true;
    const researcherIds = Array.from(
      new Set(
        visibleResearcherResults
          .map((result) => result.researcher_id ?? result.id)
          .filter((id): id is number => typeof id === "number"),
      ),
    ).filter((id) => !(id in researcherImageUrls));

    if (researcherIds.length === 0) return;

    async function loadResearcherImages() {
      const entries = await Promise.all(
        researcherIds.map(async (id) => {
          try {
            const response = await getResearcherExternalProfile(id);
            return [id, response.external_profile?.imageUrl ?? null] as const;
          } catch {
            return [id, null] as const;
          }
        }),
      );

      if (!active) return;
      setResearcherImageUrls((current) => {
        const next = { ...current };
        for (const [id, imageUrl] of entries) {
          next[id] = imageUrl;
        }
        return next;
      });
    }

    loadResearcherImages();
    return () => {
      active = false;
    };
  }, [researcherImageUrls, visibleResearcherResults]);

  const handleSearch = () => {
    setSearchPage(0);
    setCommittedQuery(query.trim());
    navigate({ to: "/", search: { q: query.trim() || undefined }, replace: true });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const toggleType = (type: PublicationType) => {
    if (!resultKinds.Publicacoes) return;
    setTypeFilters((current) => ({ ...current, [type]: !current[type] }));
  };

  const toggleResultKind = (kind: ResultKind) => {
    setResultKinds({
      Pesquisadores: kind === "Pesquisadores",
      Publicacoes: kind === "Publicacoes",
    });
  };

  const handleApplyFilters = () => {
    setFiltersApplied(true);
    setTimeout(() => setFiltersApplied(false), 1500);
  };

  const totalResults =
    visibleResearcherResults.length +
    visiblePublicationResults.length;

  const filtersPanel = (
    <div className="rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
      <div className="grid gap-4 md:grid-cols-4">
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
              className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground transition-colors focus:border-primary focus:outline-none"
            />
            <input
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              placeholder="Ate"
              inputMode="numeric"
              className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground transition-colors focus:border-primary focus:outline-none"
            />
          </div>
        </div>
        <div>
          <label className="mb-2 block text-xs font-medium text-muted-foreground">
            Tipo de Publicacao
          </label>
          <div
            className={`grid grid-cols-1 gap-1.5 text-sm transition-opacity ${
              resultKinds.Publicacoes ? "" : "opacity-45"
            }`}
          >
            {PUBLICATION_TYPES.map((type) => (
              <label key={type} className="flex items-center gap-2 text-foreground/90">
                <input
                  type="checkbox"
                  checked={typeFilters[type]}
                  onChange={() => toggleType(type)}
                  disabled={!resultKinds.Publicacoes}
                  className="h-3.5 w-3.5 accent-[var(--teal)]"
                />
                {PUBLICATION_TYPE_LABELS[type]}
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
                  type="radio"
                  name="result-kind"
                  checked={resultKinds[kind]}
                  onChange={() => toggleResultKind(kind)}
                  className="h-3.5 w-3.5 accent-[var(--teal)]"
                />
                {RESULT_KIND_LABELS[kind]}
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="mb-2 block text-xs font-medium text-muted-foreground">
            Area de Pesquisa
          </label>
          <select
            value={selectedArea}
            onChange={(e) => setSelectedArea(e.target.value)}
            className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground transition-colors focus:border-primary focus:outline-none"
          >
            <option value="">Todas as areas</option>
            {areaOptions.map((area) => (
              <option key={area} value={area}>
                {area}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background ml-[200px]">
      <header className="border-b border-border/80 bg-card/80 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-6">
          <button
            onClick={() => { setQuery(""); setCommittedQuery(""); navigate({ to: "/", search: { q: undefined }, replace: true }); }}
            className="font-serif text-xl text-foreground"
          >
            Portal de Pesquisa <span className="text-primary">Lattes</span>
          </button>
          {hasQuery && (
            <div className="flex flex-1 items-center gap-2">
              <div className="relative flex-1">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Buscar pesquisador, area ou publicacao"
                  className="w-full rounded-full border border-border bg-input py-2 pl-4 pr-10 text-sm text-foreground shadow-sm transition-colors focus:border-primary focus:outline-none"
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
                className={`shrink-0 rounded-full bg-primary p-2 text-primary-foreground shadow-sm transition-all hover:bg-primary/90 ${
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
        <div className="border-b border-border/80 bg-card/70 px-6 py-5 backdrop-blur">
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
                className="w-full rounded-full border border-border bg-input py-3 pl-5 pr-12 text-foreground shadow-[var(--shadow-card)] placeholder:text-muted-foreground transition-colors focus:border-primary focus:outline-none"
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
              className={`rounded-full bg-primary p-3 text-primary-foreground shadow-[var(--shadow-card)] transition-all hover:bg-primary/90 ${
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
            {searching
              ? "Buscando..."
              : `${totalResults} resultado${totalResults !== 1 ? "s" : ""} na pagina ${searchPage + 1}`}
          </p>
          {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

          {visibleResearcherResults.length > 0 && (
            <>
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Pesquisadores
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {visibleResearcherResults.map((result) => {
                  const researcherId = result.researcher_id ?? result.id;
                  const researcherAreas = result.areas
                    .flatMap((area) => [area.major_area, area.area, area.sub_area, area.specialty])
                    .filter((value): value is string => Boolean(value));
                  return (
                    <button
                      key={`${result.result_type}-${result.id}`}
                      onClick={() =>
                        navigate({ to: "/pesquisador/$id", params: { id: String(researcherId) } })
                      }
                      className="group flex items-start gap-4 rounded-xl border border-border/80 bg-card p-5 text-left shadow-[var(--shadow-card)] transition-all hover:-translate-y-0.5 hover:border-primary hover:shadow-[var(--shadow-card-hover)]"
                    >
                      <div className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 ring-2 ring-primary/40">
                        {researcherImageUrls[researcherId] ? (
                          <img
                            src={researcherImageUrls[researcherId] ?? ""}
                            alt={`Foto de ${result.title}`}
                            className="h-full w-full object-cover"
                            onError={() =>
                              setResearcherImageUrls((current) => ({
                                ...current,
                                [researcherId]: null,
                              }))
                            }
                          />
                        ) : (
                          <User className="h-7 w-7 text-primary" />
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-foreground group-hover:text-primary">
                          {result.title}
                        </h3>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                          {result.metadata.lattes_id
                            ? `ID Lattes: ${result.metadata.lattes_id}`
                            : resultTypeLabel(result.result_type)}
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
                          {papersByResearcher.get(researcherId) ?? 0} publicacoes
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {visiblePublicationResults.length > 0 && (
            <div className="mt-8">
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Publicacoes
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {visiblePublicationResults.map((result) => (
                  <button
                    key={`${result.result_type}-${result.id}`}
                    onClick={() => {
                      if (result.result_type === "paper") {
                        navigate({ to: "/publicacao/paper/$id", params: { id: String(result.id) }, search: { from: "search" } });
                      } else if (result.result_type === "conference_paper") {
                        navigate({
                          to: "/publicacao/conference-paper/$id",
                          params: { id: String(result.id) },
                          search: { from: "search" },
                        });
                      } else {
                        navigate({ to: "/publicacao/advising/$id", params: { id: String(result.id) }, search: { from: "search" } });
                      }
                    }}
                    className="group flex items-start gap-4 rounded-xl border border-border/80 bg-card p-5 text-left shadow-[var(--shadow-card)] transition-all hover:-translate-y-0.5 hover:border-primary hover:shadow-[var(--shadow-card-hover)]"
                  >
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
                      {result.result_type === "paper" && <FileText className="h-6 w-6 text-primary" />}
                      {result.result_type === "conference_paper" && <Presentation className="h-6 w-6 text-primary" />}
                      {result.result_type === "advising" && <GraduationCap className="h-6 w-6 text-primary" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-foreground group-hover:text-primary">
                        {result.title}
                      </h3>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {resultTypeLabel(result.result_type)} - {result.year ?? "Ano nao informado"} - score{" "}
                        {Number(result.score ?? 0).toFixed(4)}
                      </p>
                      <p className="mt-1 text-xs text-primary">
                        {String(resultSecondary(result) || result.primary_researcher?.full_name || "")}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {(searchPage > 0 || hasMoreResults) && (
            <div className="mt-6 flex items-center justify-center gap-3">
              <button
                onClick={() => setSearchPage((page) => Math.max(0, page - 1))}
                disabled={searching || searchPage === 0}
                className="flex items-center gap-1.5 rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-sm font-medium text-primary shadow-sm transition-colors hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </button>
              <span className="text-sm text-muted-foreground">
                Pagina {searchPage + 1}
              </span>
              <button
                onClick={() => setSearchPage((page) => page + 1)}
                disabled={searching || !hasMoreResults}
                className="flex items-center gap-1.5 rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-sm font-medium text-primary shadow-sm transition-colors hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Proxima
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}

          {!loading && !searching && totalResults === 0 && (
            <div className="rounded-xl border border-border/80 bg-card p-8 text-center text-sm text-muted-foreground shadow-[var(--shadow-card)]">
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
