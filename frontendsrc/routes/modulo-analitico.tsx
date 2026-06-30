import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Download, Maximize2 } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";
import {
  getAnalyticsCoauthorNetwork,
  getAnalyticsPublicationsByArea,
  getAnalyticsPublicationsByYear,
  getAnalyticsSummary,
  getAnalyticsTopResearchers,
  listResearchAreas,
  type AnalyticsAreaRow,
  type AnalyticsCoauthorNetwork,
  type AnalyticsResearcherRow,
  type AnalyticsSummary,
  type AnalyticsYearRow,
  type ResearchArea,
} from "@/lib/api";

export const Route = createFileRoute("/modulo-analitico")({
  head: () => ({
    meta: [{ title: "Modulo Analitico - Lattes" }],
  }),
  component: ModuloAnalitico,
});

type YearRow = {
  year: number;
  paper: number;
  conference: number;
  advising: number;
};

type AreaSlice = {
  label: string;
  value: number;
  color: string;
};

const ALL_TYPES = ["Paper", "Conference Paper", "Advising"];
const AREA_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function areaLabel(area: ResearchArea) {
  return area.area ?? area.major_area ?? area.sub_area ?? area.specialty ?? "Area nao informada";
}

function typeParam(type: string) {
  if (type === "Conference Paper") return "conference_paper";
  if (type === "Advising") return "advising";
  return "paper";
}

function typeLabel(type: string) {
  if (type === "conference_paper") return "Trabalho em evento";
  if (type === "advising") return "Orientacao";
  return "Artigo de periodico";
}

function buildYearRows(rows: AnalyticsYearRow[]) {
  const map = new Map<number, YearRow>();
  for (const row of rows) {
    const current = map.get(row.year) ?? {
      year: row.year,
      paper: 0,
      conference: 0,
      advising: 0,
    };

    if (row.type === "paper") current.paper = row.unique_publications;
    if (row.type === "conference_paper") current.conference = row.unique_publications;
    if (row.type === "advising") current.advising = row.unique_publications;
    map.set(row.year, current);
  }

  return Array.from(map.values()).sort((a, b) => a.year - b.year);
}

function buildAreaSlices(rows: AnalyticsAreaRow[]) {
  return rows.slice(0, 5).map((row, index) => ({
    label: row.area,
    value: row.unique_publications,
    color: AREA_COLORS[index % AREA_COLORS.length],
  }));
}

function emptySummary(): AnalyticsSummary {
  return {
    total_researchers: 0,
    total_unique_publications: 0,
    total_authorships: 0,
    collaborative_publications: 0,
    productions_by_type: {},
    papers_without_doi: 0,
    conference_papers_without_doi: 0,
    duplicate_doi_groups: 0,
    average_curriculum_update_year: null,
  };
}

function ModuloAnalitico() {
  const [yearRange, setYearRange] = useState({ from: 2018, to: 2026 });
  const [selectedTypes, setSelectedTypes] = useState<string[]>([...ALL_TYPES]);
  const [selectedArea, setSelectedArea] = useState<string>("Todas as Areas");
  const [areaOptions, setAreaOptions] = useState<string[]>(["Todas as Areas"]);
  const [summary, setSummary] = useState<AnalyticsSummary>(emptySummary);
  const [yearRows, setYearRows] = useState<AnalyticsYearRow[]>([]);
  const [areaRows, setAreaRows] = useState<AnalyticsAreaRow[]>([]);
  const [topResearchers, setTopResearchers] = useState<AnalyticsResearcherRow[]>([]);
  const [coauthorNetwork, setCoauthorNetwork] = useState<AnalyticsCoauthorNetwork>({
    nodes: [],
    edges: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadAreas() {
      try {
        const areas = await listResearchAreas();
        if (!active) return;

        const labels = Array.from(new Set(areas.map(areaLabel))).sort();
        setAreaOptions(["Todas as Areas", ...labels]);
      } catch {
        if (active) setAreaOptions(["Todas as Areas"]);
      }
    }

    loadAreas();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadAnalyticsData() {
      const filters = {
        yearFrom: yearRange.from,
        yearTo: yearRange.to,
        area: selectedArea === "Todas as Areas" ? undefined : selectedArea,
        types: selectedTypes.map(typeParam),
      };

      try {
        setLoading(true);
        const [summaryData, byYear, byArea, topData, networkData] = await Promise.all([
          getAnalyticsSummary(filters),
          getAnalyticsPublicationsByYear(filters),
          getAnalyticsPublicationsByArea({ ...filters, limit: 5 }),
          getAnalyticsTopResearchers({ ...filters, limit: 8 }),
          getAnalyticsCoauthorNetwork({ ...filters, limit: 50 }),
        ]);

        if (!active) return;

        setSummary(summaryData);
        setYearRows(byYear);
        setAreaRows(byArea);
        setTopResearchers(topData);
        setCoauthorNetwork(networkData);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Nao foi possivel carregar os dados.");
      } finally {
        if (active) setLoading(false);
      }
    }

    loadAnalyticsData();
    return () => {
      active = false;
    };
  }, [selectedArea, selectedTypes, yearRange]);

  const yearData = useMemo(() => buildYearRows(yearRows), [yearRows]);
  const areaData = useMemo<AreaSlice[]>(() => buildAreaSlices(areaRows), [areaRows]);

  const maxBar = Math.max(1, ...topResearchers.map((researcher) => researcher.authorships));
  const maxYear = Math.max(
    1,
    ...yearData.map((row) => row.paper + row.conference + row.advising),
  );
  const totalArea = areaData.reduce((sum, area) => sum + area.value, 0) || 1;
  const internalCoauthorships = coauthorNetwork.edges.reduce(
    (sum, edge) => sum + edge.weight,
    0,
  );

  let cumulative = 0;
  const donutSegments = areaData.map((area) => {
    const percent = Math.round((area.value / totalArea) * 100);
    const start = cumulative;
    cumulative += percent;
    return { ...area, percent, start, end: cumulative };
  });

  return (
    <div className="min-h-screen bg-background">
      <FiltrosPanel
        showExport
        yearRange={yearRange}
        onYearRangeChange={setYearRange}
        selectedTypes={selectedTypes}
        onTypesChange={setSelectedTypes}
        selectedArea={selectedArea}
        onAreaChange={setSelectedArea}
        areaOptions={areaOptions}
      />
      <main className="ml-[200px] mr-[250px] px-8 py-8">
        {error && (
          <div className="mb-4 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <section className="grid grid-cols-3 gap-4">
          {[
            { label: "PESQUISADORES", value: summary.total_researchers },
            { label: "PRODUCOES UNICAS", value: summary.total_unique_publications },
            { label: "AUTORIAS", value: summary.total_authorships },
            { label: "PRODUCOES COLABORATIVAS", value: summary.collaborative_publications },
            { label: "COAUTORIAS INTERNAS", value: internalCoauthorships },
            {
              label: "SEM DOI",
              value: summary.papers_without_doi + summary.conference_papers_without_doi,
            },
          ].map((stat) => (
            <div key={stat.label} className="rounded-xl border border-border/80 bg-card px-5 py-4 shadow-[var(--shadow-card)]">
              <p className="text-[10px] font-semibold tracking-wider text-muted-foreground">
                {stat.label}
              </p>
              <p className="mt-1 font-serif text-3xl text-primary">
                {loading ? "..." : Number(stat.value ?? 0).toLocaleString("pt-BR")}
              </p>
            </div>
          ))}
        </section>

        <section className="mt-6 rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Producoes por tipo</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(summary.productions_by_type).map(([type, values]) => (
              <div key={type} className="rounded-md border border-border/80 bg-secondary p-3">
                <p className="text-xs text-muted-foreground">{typeLabel(type)}</p>
                <p className="mt-1 text-2xl font-semibold text-primary">
                  {values.unique_publications.toLocaleString("pt-BR")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {values.authorships.toLocaleString("pt-BR")} autorias
                </p>
              </div>
            ))}
            {!loading && Object.keys(summary.productions_by_type).length === 0 && (
              <p className="text-xs text-muted-foreground">Nenhuma producao para os filtros atuais.</p>
            )}
          </div>
        </section>

        <section className="mt-6 rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Pesquisadores mais produtivos</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="space-y-3">
            {topResearchers.map((bar) => (
              <div key={bar.researcher_id} className="flex items-center gap-3 text-sm">
                <span className="w-48 shrink-0 truncate text-muted-foreground">{bar.full_name}</span>
                <div className="relative h-5 flex-1 overflow-hidden rounded bg-secondary shadow-inner">
                  <div
                    className="h-full rounded bg-primary"
                    style={{ width: `${(bar.authorships / maxBar) * 100}%` }}
                  />
                </div>
                <span className="w-20 text-right text-xs text-foreground">
                  {bar.authorships} autorias
                </span>
              </div>
            ))}
            {!loading && topResearchers.length === 0 && (
              <p className="text-xs text-muted-foreground">Nenhum resultado para os filtros atuais.</p>
            )}
          </div>
        </section>

        <section className="mt-6 rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Producoes por area</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="flex items-center gap-8">
            <Donut segments={donutSegments} />
            <div className="flex-1 space-y-2">
              {donutSegments.map((segment) => (
                <div key={segment.label} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-foreground">
                    <span
                      className="h-3 w-3 rounded-sm"
                      style={{ background: segment.color }}
                    />
                    {segment.label}
                  </span>
                  <span className="text-muted-foreground">{segment.percent}%</span>
                </div>
              ))}
              {!loading && donutSegments.length === 0 && (
                <p className="text-xs text-muted-foreground">Nenhuma area encontrada.</p>
              )}
            </div>
          </div>
        </section>

        <section className="mt-6 rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Producoes por ano</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="mb-3 flex flex-wrap gap-3 text-xs">
            {[
              { label: "Artigo de periodico", color: "var(--chart-1)" },
              { label: "Trabalho em evento", color: "var(--chart-2)" },
              { label: "Orientacao", color: "var(--chart-3)" },
            ].map((item) => (
              <span key={item.label} className="flex items-center gap-1.5 text-foreground">
                <span className="h-3 w-3 rounded-sm" style={{ background: item.color }} />
                {item.label}
              </span>
            ))}
          </div>
          <div className="flex h-64 items-stretch gap-3 border-l border-b border-border pl-2 pb-2 pt-2">
            {yearData.map((row) => {
              const total = row.paper + row.conference + row.advising;
              const height = total > 0 ? (total / maxYear) * 100 : 0;
              return (
                <div key={row.year} className="flex h-full min-w-8 flex-1 flex-col items-center justify-end gap-1">
                  <div
                    className="flex w-full max-w-12 flex-col-reverse overflow-hidden rounded-t bg-secondary/60"
                    style={{ height: total > 0 ? `${Math.max(height, 4)}%` : "2px" }}
                    title={`${row.year}: ${total} producoes`}
                  >
                    {total > 0 && (
                      <>
                        <div style={{ height: `${(row.paper / total) * 100}%`, background: "var(--chart-1)" }} />
                        <div style={{ height: `${(row.conference / total) * 100}%`, background: "var(--chart-2)" }} />
                        <div style={{ height: `${(row.advising / total) * 100}%`, background: "var(--chart-3)" }} />
                      </>
                    )}
                  </div>
                  <span className="text-[10px] text-muted-foreground">{row.year}</span>
                </div>
              );
            })}
            {!loading && yearData.length === 0 && (
              <p className="self-center text-xs text-muted-foreground">Nenhum dado no intervalo selecionado.</p>
            )}
          </div>
        </section>

        <section className="mt-6 rounded-xl border border-border/80 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Coautorias internas</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="space-y-2">
            {coauthorNetwork.edges.slice(0, 8).map((edge) => {
              const source = coauthorNetwork.nodes.find((node) => node.id === edge.source);
              const target = coauthorNetwork.nodes.find((node) => node.id === edge.target);
              return (
                <div
                  key={`${edge.source}-${edge.target}`}
                  className="flex items-center justify-between rounded-md border border-border/60 bg-secondary px-3 py-2 text-sm"
                >
                  <span className="truncate text-foreground">
                    {source?.label ?? edge.source} / {target?.label ?? edge.target}
                  </span>
                  <span className="ml-3 shrink-0 text-xs text-muted-foreground">
                    {edge.weight} producoes
                  </span>
                </div>
              );
            })}
            {!loading && coauthorNetwork.edges.length === 0 && (
              <p className="text-xs text-muted-foreground">Nenhuma coautoria interna encontrada.</p>
            )}
          </div>
        </section>

        <div className="mt-6 flex items-center gap-3">
          <Link
            to="/"
            className="rounded-md border border-border bg-secondary px-4 py-2 text-sm text-foreground transition-colors hover:border-primary hover:bg-accent"
          >
            Voltar ao Inicio
          </Link>
          <button className="flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary transition-colors hover:bg-primary/20">
            <Download className="h-4 w-4" /> Exportar relatorio
          </button>
        </div>

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

function Donut({
  segments,
}: {
  segments: { label: string; value: number; color: string; percent: number; start: number; end: number }[];
}) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  return (
    <svg width="160" height="160" viewBox="0 0 160 160" className="shrink-0">
      <g transform="translate(80 80) rotate(-90)">
        <circle r={radius} fill="none" stroke="var(--secondary)" strokeWidth="22" />
        {segments.map((segment) => {
          const dash = ((segment.end - segment.start) / 100) * circumference;
          const offset = (segment.start / 100) * circumference;
          return (
            <circle
              key={segment.label}
              r={radius}
              fill="none"
              stroke={segment.color}
              strokeWidth="22"
              strokeDasharray={`${dash} ${circumference - dash}`}
              strokeDashoffset={-offset}
            />
          );
        })}
      </g>
    </svg>
  );
}
