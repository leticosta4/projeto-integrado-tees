import {
  createFileRoute,
  Link,
  notFound,
  useNavigate,
} from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { BarChart3, Download, User } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";
import {
  getResearcher,
  listAdvisings,
  listConferencePapers,
  listPapers,
  listResearchAreas,
  type Advising,
  type ConferencePaper,
  type Paper,
  type ResearchArea,
  type Researcher,
} from "@/lib/api";

export const Route = createFileRoute("/pesquisador/$id")({
  head: ({ params }) => ({
    meta: [{ title: `Pesquisador ${params.id} - Lattes` }],
  }),
  loader: async ({ params }) => {
    try {
      const [researcher, papers, areas, conferencePapers, advisings] =
        await Promise.all([
          getResearcher(params.id),
          listPapers({ researcher_id: params.id }),
          listResearchAreas({ researcher_id: params.id }),
          listConferencePapers({ researcher_id: params.id }),
          listAdvisings({ researcher_id: params.id }),
        ]);
      return { researcher, papers, areas, conferencePapers, advisings };
    } catch {
      throw notFound();
    }
  },
  component: ResearcherProfile,
  notFoundComponent: () => (
    <div className="flex min-h-screen items-center justify-center text-foreground">
      Pesquisador nao encontrado.
    </div>
  ),
  errorComponent: ({ error }) => (
    <div className="flex min-h-screen items-center justify-center text-destructive">
      {error.message}
    </div>
  ),
});

function areaLabel(area: ResearchArea) {
  return (
    area.specialty ??
    area.sub_area ??
    area.area ??
    area.major_area ??
    "Area nao informada"
  );
}

function researcherDescription(researcher: Researcher) {
  const firstCitationName = researcher.citation_name
    ? researcher.citation_name.split(";")[0].trim()
    : null;

  const parts = [
    firstCitationName ? `Nome em citacoes: ${firstCitationName}` : null,
    researcher.nationality ? `Nacionalidade: ${researcher.nationality}` : null,
    researcher.birth_state
      ? `UF de nascimento: ${researcher.birth_state}`
      : null,
    researcher.update_date
      ? `Curriculo atualizado em ${researcher.update_date}`
      : null,
  ].filter(Boolean);

  return parts.length > 0
    ? parts.join(" - ")
    : "Pesquisador importado a partir dos dados do Curriculo Lattes.";
}

type PublicationItem =
  | { kind: "paper"; data: Paper }
  | { kind: "conference-paper"; data: ConferencePaper }
  | { kind: "advising"; data: Advising };

const PROFILE_PUBLICATION_TYPES = ["Paper", "Conference Paper", "Advising"];
const DEFAULT_AREA_OPTION = "Todas as Areas";

function publicationLabel(kind: PublicationItem["kind"]) {
  if (kind === "paper") return "Paper";
  if (kind === "conference-paper") return "Conference Paper";
  return "Orientacao";
}

function publicationTypeName(kind: PublicationItem["kind"]) {
  if (kind === "paper") return "Paper";
  if (kind === "conference-paper") return "Conference Paper";
  return "Advising";
}

function publicationSecondary(item: PublicationItem): string {
  if (item.kind === "paper") return item.data.journal ?? item.data.nature ?? "";
  if (item.kind === "conference-paper")
    return item.data.event_name ?? item.data.nature ?? "";
  return item.data.advising_type ?? item.data.level ?? "";
}

function exportPublicationsCSV(items: PublicationItem[]) {
  const rows = [["Tipo", "Titulo", "Ano", "Detalhes"]];
  for (const item of items) {
    rows.push([
      publicationLabel(item.kind),
      item.data.title,
      String(item.data.year ?? ""),
      publicationSecondary(item),
    ]);
  }
  const csv = rows
    .map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(","))
    .join("\n");
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "publicacoes.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function navigateToPublication(
  navigate: ReturnType<typeof useNavigate>,
  item: PublicationItem,
) {
  if (item.kind === "paper") {
    navigate({
      to: "/publicacao/paper/$id",
      params: { id: String(item.data.id) },
      search: { from: "" },
    });
  } else if (item.kind === "conference-paper") {
    navigate({
      to: "/publicacao/conference-paper/$id",
      params: { id: String(item.data.id) },
      search: { from: "" },
    });
  } else {
    navigate({
      to: "/publicacao/advising/$id",
      params: { id: String(item.data.id) },
      search: { from: "" },
    });
  }
}

function ResearcherProfile() {
  const { researcher, papers, areas, conferencePapers, advisings } =
    Route.useLoaderData() as {
      researcher: Researcher;
      papers: Paper[];
      areas: ResearchArea[];
      conferencePapers: ConferencePaper[];
      advisings: Advising[];
    };
  const navigate = useNavigate();

  const allPublications: PublicationItem[] = [
    ...papers.map((data) => ({ kind: "paper" as const, data })),
    ...conferencePapers.map((data) => ({
      kind: "conference-paper" as const,
      data,
    })),
    ...advisings.map((data) => ({ kind: "advising" as const, data })),
  ].sort((a, b) => (b.data.year ?? 0) - (a.data.year ?? 0));

  const publicationYears = allPublications
    .map((item) => item.data.year)
    .filter((year): year is number => typeof year === "number");
  const initialYearFrom = publicationYears.length ? Math.min(...publicationYears) : 1900;
  const initialYearTo = publicationYears.length
    ? Math.max(...publicationYears)
    : new Date().getFullYear();

  const [filtersOpen, setFiltersOpen] = useState(true);
  const [visibleCount, setVisibleCount] = useState(20);
  const [yearRange, setYearRange] = useState({
    from: initialYearFrom,
    to: initialYearTo,
  });
  const [selectedTypes, setSelectedTypes] = useState<string[]>([
    ...PROFILE_PUBLICATION_TYPES,
  ]);
  const [selectedArea, setSelectedArea] = useState(DEFAULT_AREA_OPTION);

  const areaOptions = useMemo(() => {
    const labels = Array.from(new Set(areas.map(areaLabel))).sort();
    return [DEFAULT_AREA_OPTION, ...labels];
  }, [areas]);

  const areaMatches =
    selectedArea === DEFAULT_AREA_OPTION ||
    areaOptions.includes(selectedArea);

  const filteredPublications = allPublications.filter((item) => {
    const year = item.data.year;
    const matchesYear =
      typeof year === "number" &&
      (year >= yearRange.from && year <= yearRange.to);
    const matchesType = selectedTypes.includes(publicationTypeName(item.kind));

    return matchesYear && matchesType && areaMatches;
  });

  useEffect(() => {
    setVisibleCount(20);
  }, [selectedArea, selectedTypes, yearRange]);

  const filteredPapers = filteredPublications.filter((item) => item.kind === "paper");
  const filteredConferencePapers = filteredPublications.filter(
    (item) => item.kind === "conference-paper",
  );
  const filteredAdvisings = filteredPublications.filter(
    (item) => item.kind === "advising",
  );
  const totalPublications = filteredPublications.length;
  const visiblePublications = filteredPublications.slice(0, visibleCount);

  return (
    <div className="min-h-screen bg-background">
      <FiltrosPanel
        isOpen={filtersOpen}
        onToggle={() => setFiltersOpen((value) => !value)}
        yearRange={yearRange}
        onYearRangeChange={setYearRange}
        selectedTypes={selectedTypes}
        onTypesChange={setSelectedTypes}
        selectedArea={selectedArea}
        onAreaChange={setSelectedArea}
        areaOptions={areaOptions}
      />
      <main
        className={`ml-[200px] ${filtersOpen ? "mr-[250px]" : "mr-[40px]"} px-8 py-8`}
      >
        <section className="rounded-xl border border-border/80 bg-card p-6 shadow-[var(--shadow-card)]">
          <div className="flex items-start gap-5">
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
              <User className="h-10 w-10 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="font-serif text-2xl text-foreground">
                  {researcher.full_name}
                </h1>
                <span className="rounded-full bg-primary/15 px-2.5 py-0.5 text-xs text-primary">
                  Pesquisador
                </span>
              </div>
              <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
                {researcherDescription(researcher)}
              </p>
              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                <span>ID Lattes: {researcher.lattes_id}</span>
                {researcher.orcid && <span>ORCID: {researcher.orcid}</span>}
              </div>
            </div>
          </div>
        </section>

        <section className="mt-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Producoes
          </h2>
          <div className="mt-2 flex gap-6">
            <div>
              <p className="font-serif text-4xl text-foreground">
                {filteredPapers.length}
              </p>
              <p className="text-xs text-muted-foreground">Papers</p>
            </div>
            <div>
              <p className="font-serif text-4xl text-foreground">
                {filteredConferencePapers.length}
              </p>
              <p className="text-xs text-muted-foreground">Conference Papers</p>
            </div>
            <div>
              <p className="font-serif text-4xl text-foreground">
                {filteredAdvisings.length}
              </p>
              <p className="text-xs text-muted-foreground">Orientacoes</p>
            </div>
          </div>
        </section>

        <section className="mt-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Areas de Atuacao
          </h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {areas.length > 0 ? (
              areas.map((area) => (
                <span
                  key={area.id}
                  className="rounded-full border border-primary/40 bg-primary/10 px-3 py-1 text-sm text-primary"
                >
                  {areaLabel(area)}
                </span>
              ))
            ) : (
              <span className="text-sm text-muted-foreground">
                Nenhuma area cadastrada.
              </span>
            )}
          </div>
        </section>

        <section className="mt-8 rounded-xl border border-border/80 bg-card p-6 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-foreground">
              Producoes Cientificas
            </h2>
            <button
              onClick={() => exportPublicationsCSV(filteredPublications)}
              className="flex items-center gap-1.5 rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground transition-colors hover:border-primary hover:bg-accent"
            >
              <Download className="h-3.5 w-3.5" /> Exportar CSV
            </button>
          </div>
          <div className="divide-y divide-border">
            {visiblePublications.map((item) => (
              <button
                key={`${item.kind}-${item.data.id}`}
                onClick={() => navigateToPublication(navigate, item)}
                className="flex w-full items-center gap-4 rounded-md px-2 py-3 text-left text-sm transition-colors hover:bg-primary/5"
              >
                <span className="w-12 shrink-0 text-muted-foreground">
                  {item.data.year ?? "-"}
                </span>
                <span className="w-32 shrink-0 rounded bg-secondary px-2 py-0.5 text-center text-xs text-foreground">
                  {publicationLabel(item.kind)}
                </span>
                <span className="flex-1 text-foreground/90">
                  {item.data.title}
                </span>
                <span className="text-xs text-primary">
                  {publicationSecondary(item)}
                </span>
              </button>
            ))}
            {totalPublications === 0 && (
              <p className="py-6 text-sm text-muted-foreground">
                Nenhuma publicacao cadastrada para este pesquisador.
              </p>
            )}
          </div>
          {visibleCount < totalPublications && (
            <button
              onClick={() => setVisibleCount((c) => c + 20)}
              className="mt-4 text-xs text-muted-foreground hover:text-primary"
            >
              Exibindo {visibleCount} de {totalPublications} itens — carregar
              mais
            </button>
          )}
        </section>

        <section className="mt-8">
          <Link
            to="/modulo-analitico"
            className="inline-flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
          >
            <BarChart3 className="h-4 w-4" />
            Abrir Modulo Analitico
          </Link>
        </section>

        <footer className="mt-10 flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground">
          <span>2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">
            Termos de uso
          </a>
        </footer>
      </main>
    </div>
  );
}
