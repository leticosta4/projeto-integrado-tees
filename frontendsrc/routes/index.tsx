import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { FileText, Search, SlidersHorizontal, User } from "lucide-react";
import {
  listPapers,
  listResearchAreas,
  listResearchers,
  searchPapers,
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
  const [areas, setAreas] = useState<ResearchArea[]>([]);
  const [paperResults, setPaperResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const hasQuery = committedQuery.trim().length > 0;

  useEffect(() => {
    let active = true;

    async function loadInitialData() {
      try {
        setLoading(true);
        const [researcherData, paperData, areaData] = await Promise.all([
          listResearchers(),
          listPapers(),
          listResearchAreas(),
        ]);

        if (!active) return;
        setResearchers(researcherData);
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

  const researcherResults = useMemo(() => {
    if (!hasQuery) return [];
    const lowered = normalize(committedQuery);

    return researchers.filter((researcher) => {
      const researcherAreas = uniqueAreas(areasByResearcher.get(researcher.id) ?? []);
      return (
        normalize(researcher.full_name).includes(lowered) ||
        normalize(researcher.citation_name).includes(lowered) ||
        normalize(researcher.lattes_id).includes(lowered) ||
        researcherAreas.some((area) => normalize(area).includes(lowered))
      );
    });
  }, [areasByResearcher, committedQuery, hasQuery, researchers]);

  const handleSearch = () => {
    setCommittedQuery(query.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const totalResults = researcherResults.length + paperResults.length;

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
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Buscar pesquisador, area ou publicacao"
                  className="w-full rounded-full border border-border bg-input py-2 pl-10 pr-4 text-sm text-foreground focus:border-primary focus:outline-none"
                />
              </div>
              <button
                onClick={handleSearch}
                className="rounded-md border border-border bg-secondary px-3 py-2 text-xs text-foreground hover:border-primary"
              >
                Buscar
              </button>
            </div>
          )}
        </div>
      </header>

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

          {showFilters && (
            <div className="mt-6 w-full max-w-2xl rounded-xl border border-border bg-card p-5">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-xs font-medium text-muted-foreground">
                    Intervalo de Anos
                  </label>
                  <div className="flex gap-2">
                    <input
                      defaultValue="2018"
                      placeholder="De"
                      className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
                    />
                    <input
                      defaultValue="2024"
                      placeholder="Ate"
                      className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs font-medium text-muted-foreground">
                    Tipo de Publicacao
                  </label>
                  <div className="grid grid-cols-2 gap-1.5 text-sm">
                    {["Paper", "Conference Paper", "Advising"].map((type) => (
                      <label key={type} className="flex items-center gap-2 text-foreground/90">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="h-3.5 w-3.5 accent-[var(--teal)]"
                        />
                        {type}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleSearch}
                  className="rounded-md bg-primary px-4 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                >
                  Aplicar
                </button>
              </div>
            </div>
          )}

          {loading && <p className="mt-6 text-sm text-muted-foreground">Carregando dados do banco...</p>}
          {error && <p className="mt-6 max-w-xl text-center text-sm text-destructive">{error}</p>}
        </section>
      ) : (
        <section className="mx-auto max-w-6xl px-6 py-8">
          <p className="mb-4 text-sm text-muted-foreground">
            {searching ? "Buscando..." : `${totalResults} resultado${totalResults !== 1 ? "s" : ""} encontrado${totalResults !== 1 ? "s" : ""}`}
          </p>
          {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

          {researcherResults.length > 0 && (
            <>
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Pesquisadores
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {researcherResults.map((researcher) => {
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

          {paperResults.length > 0 && (
            <div className="mt-8">
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Publicacoes
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {paperResults.map(({ paper, score }) => (
                  <button
                    key={paper.id}
                    onClick={() =>
                      navigate({ to: "/pesquisador/$id", params: { id: String(paper.researcher_id) } })
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
