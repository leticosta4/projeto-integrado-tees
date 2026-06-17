import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Download, Maximize2 } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";
import {
  listAdvisings,
  listConferencePapers,
  listPapers,
  listResearchAreas,
  listResearchers,
  type ResearchArea,
  type Researcher,
} from "@/lib/api";

export const Route = createFileRoute("/modulo-analitico")({
  head: () => ({
    meta: [{ title: "Modulo Analitico - Lattes" }],
  }),
  component: ModuloAnalitico,
});

type PublicationRecord = {
  researcherId: number;
  year: number | null;
  type: "Paper" | "Conference Paper" | "Advising";
};

type YearRow = {
  year: number;
  paper: number;
  conference: number;
  advising: number;
};

type ResearcherBar = {
  name: string;
  value: number;
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

function buildResearcherAreaMap(areas: ResearchArea[]) {
  const map = new Map<number, string[]>();
  for (const area of areas) {
    const labels = map.get(area.researcher_id) ?? [];
    const label = areaLabel(area);
    if (!labels.includes(label)) labels.push(label);
    map.set(area.researcher_id, labels);
  }
  return map;
}

function ModuloAnalitico() {
  const [yearRange, setYearRange] = useState({ from: 2018, to: 2026 });
  const [selectedTypes, setSelectedTypes] = useState<string[]>([...ALL_TYPES]);
  const [selectedArea, setSelectedArea] = useState<string>("Todas as Areas");
  const [researchers, setResearchers] = useState<Researcher[]>([]);
  const [areas, setAreas] = useState<ResearchArea[]>([]);
  const [records, setRecords] = useState<PublicationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadAnalyticsData() {
      try {
        setLoading(true);
        const [researcherData, areaData, paperData, conferenceData, advisingData] =
          await Promise.all([
            listResearchers(),
            listResearchAreas(),
            listPapers(),
            listConferencePapers(),
            listAdvisings(),
          ]);

        if (!active) return;

        setResearchers(researcherData);
        setAreas(areaData);
        setRecords([
          ...paperData.map((paper) => ({
            researcherId: paper.researcher_id,
            year: paper.year ?? null,
            type: "Paper" as const,
          })),
          ...conferenceData.map((paper) => ({
            researcherId: paper.researcher_id,
            year: paper.year ?? paper.event_year ?? null,
            type: "Conference Paper" as const,
          })),
          ...advisingData.map((advising) => ({
            researcherId: advising.researcher_id,
            year: advising.year ?? null,
            type: "Advising" as const,
          })),
        ]);
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
  }, []);

  const researcherById = useMemo(() => {
    return new Map(researchers.map((researcher) => [researcher.id, researcher]));
  }, [researchers]);

  const areasByResearcher = useMemo(() => buildResearcherAreaMap(areas), [areas]);

  const areaOptions = useMemo(() => {
    const labels = Array.from(new Set(areas.map(areaLabel))).sort();
    return ["Todas as Areas", ...labels];
  }, [areas]);

  const filteredRecords = useMemo(() => {
    return records.filter((record) => {
      const inYear =
        record.year == null || (record.year >= yearRange.from && record.year <= yearRange.to);
      const inType = selectedTypes.includes(record.type);
      const researcherAreas = areasByResearcher.get(record.researcherId) ?? [];
      const inArea =
        selectedArea === "Todas as Areas" || researcherAreas.includes(selectedArea);
      return inYear && inType && inArea;
    });
  }, [areasByResearcher, records, selectedArea, selectedTypes, yearRange]);

  const yearData = useMemo<YearRow[]>(() => {
    const rows = new Map<number, YearRow>();
    for (const record of filteredRecords) {
      if (record.year == null) continue;
      const row = rows.get(record.year) ?? {
        year: record.year,
        paper: 0,
        conference: 0,
        advising: 0,
      };
      if (record.type === "Paper") row.paper += 1;
      if (record.type === "Conference Paper") row.conference += 1;
      if (record.type === "Advising") row.advising += 1;
      rows.set(record.year, row);
    }
    return Array.from(rows.values()).sort((a, b) => a.year - b.year);
  }, [filteredRecords]);

  const researcherBars = useMemo<ResearcherBar[]>(() => {
    const counts = new Map<number, number>();
    for (const record of filteredRecords) {
      counts.set(record.researcherId, (counts.get(record.researcherId) ?? 0) + 1);
    }
    return Array.from(counts.entries())
      .map(([researcherId, value]) => ({
        name: researcherById.get(researcherId)?.full_name ?? `Pesquisador ${researcherId}`,
        value,
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);
  }, [filteredRecords, researcherById]);

  const areaData = useMemo<AreaSlice[]>(() => {
    const counts = new Map<string, number>();
    for (const record of filteredRecords) {
      const labels = areasByResearcher.get(record.researcherId) ?? ["Area nao informada"];
      for (const label of labels) {
        if (selectedArea !== "Todas as Areas" && label !== selectedArea) continue;
        counts.set(label, (counts.get(label) ?? 0) + 1);
      }
    }

    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([label, value], index) => ({
        label,
        value,
        color: AREA_COLORS[index % AREA_COLORS.length],
      }));
  }, [areasByResearcher, filteredRecords, selectedArea]);

  const maxBar = Math.max(1, ...researcherBars.map((researcher) => researcher.value));
  const maxYear = Math.max(
    1,
    ...yearData.map((row) => row.paper + row.conference + row.advising),
  );
  const totalArea = areaData.reduce((sum, area) => sum + area.value, 0) || 1;

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
            { label: "AREAS DE PESQUISA", value: String(areaData.length) },
            { label: "PESQUISADORES", value: String(researcherBars.length) },
            {
              label: "PRODUCOES",
              value: loading ? "..." : filteredRecords.length.toLocaleString("pt-BR"),
            },
          ].map((stat) => (
            <div key={stat.label} className="rounded-xl border border-border bg-card px-5 py-4">
              <p className="text-[10px] font-semibold tracking-wider text-muted-foreground">
                {stat.label}
              </p>
              <p className="mt-1 font-serif text-3xl text-primary">{stat.value}</p>
            </div>
          ))}
        </section>

        <section className="mt-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Producoes por pesquisador</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="space-y-3">
            {researcherBars.map((bar) => (
              <div key={bar.name} className="flex items-center gap-3 text-sm">
                <span className="w-40 shrink-0 truncate text-muted-foreground">{bar.name}</span>
                <div className="relative h-5 flex-1 overflow-hidden rounded bg-secondary">
                  <div
                    className="h-full rounded bg-primary"
                    style={{ width: `${(bar.value / maxBar) * 100}%` }}
                  />
                </div>
                <span className="w-10 text-right text-xs text-foreground">{bar.value}</span>
              </div>
            ))}
            {!loading && researcherBars.length === 0 && (
              <p className="text-xs text-muted-foreground">Nenhum resultado para os filtros atuais.</p>
            )}
          </div>
        </section>

        <section className="mt-6 rounded-xl border border-border bg-card p-5">
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

        <section className="mt-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Producoes por ano</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="mb-3 flex flex-wrap gap-3 text-xs">
            {[
              { label: "Paper", color: "var(--chart-1)" },
              { label: "Conference Paper", color: "var(--chart-2)" },
              { label: "Advising", color: "var(--chart-3)" },
            ].map((item) => (
              <span key={item.label} className="flex items-center gap-1.5 text-foreground">
                <span className="h-3 w-3 rounded-sm" style={{ background: item.color }} />
                {item.label}
              </span>
            ))}
          </div>
          <div className="flex h-64 items-end gap-3 border-l border-b border-border pl-2 pb-2 pt-2">
            {yearData.map((row) => {
              const total = row.paper + row.conference + row.advising;
              const height = total > 0 ? (total / maxYear) * 100 : 0;
              return (
                <div key={row.year} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="flex w-full flex-col-reverse overflow-hidden rounded-t"
                    style={{ height: `${height}%` }}
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

        <div className="mt-6 flex items-center gap-3">
          <Link
            to="/"
            className="rounded-md border border-border bg-secondary px-4 py-2 text-sm text-foreground hover:border-primary"
          >
            Voltar ao Inicio
          </Link>
          <button className="flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary hover:bg-primary/20">
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
