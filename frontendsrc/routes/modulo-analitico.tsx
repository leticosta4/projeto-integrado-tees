import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Maximize2, Download } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";

export const Route = createFileRoute("/modulo-analitico")({
  head: () => ({
    meta: [{ title: "Módulo Analítico — Lattes" }],
  }),
  component: ModuloAnalitico,
});

type YearRow = { year: number; a1: number; a2: number; a3: number; outras: number };

const yearDataRaw: YearRow[] = [
  { year: 2018, a1: 320, a2: 240, a3: 180, outras: 90 },
  { year: 2019, a1: 410, a2: 280, a3: 200, outras: 110 },
  { year: 2020, a1: 520, a2: 330, a3: 220, outras: 140 },
  { year: 2021, a1: 600, a2: 380, a3: 250, outras: 170 },
  { year: 2022, a1: 720, a2: 440, a3: 290, outras: 200 },
  { year: 2023, a1: 880, a2: 510, a3: 330, outras: 230 },
  { year: 2024, a1: 1000, a2: 580, a3: 360, outras: 260 },
];

type ResearcherBar = { name: string; value: number; type: string; area: string };
const researcherBarsRaw: ResearcherBar[] = [
  { name: "Pesquisador 1", value: 293, type: "Paper", area: "Área 1" },
  { name: "Pesquisador 2", value: 214, type: "Conference Paper", area: "Área 2" },
  { name: "Pesquisador 3", value: 119, type: "Advising", area: "Área 3" },
  { name: "Pesquisador 4", value: 52, type: "Paper", area: "Área 2" },
  { name: "Pesquisador 5", value: 37, type: "Conference Paper", area: "Área 1" },
  { name: "Outros (52)", value: 86, type: "Advising", area: "Área 1" },
];

type AreaSlice = { label: string; value: number; color: string };
const areaDataRaw: AreaSlice[] = [
  { label: "Área 1", value: 40, color: "var(--chart-1)" },
  { label: "Área 2", value: 30, color: "var(--chart-2)" },
  { label: "Área 3", value: 20, color: "var(--chart-3)" },
  { label: "Outras (5)", value: 10, color: "var(--chart-4)" },
];

const ALL_TYPES = ["Paper", "Conference Paper", "Advising"];

function ModuloAnalitico() {
  const [yearRange, setYearRange] = useState({ from: 2018, to: 2024 });
  const [selectedTypes, setSelectedTypes] = useState<string[]>([...ALL_TYPES]);
  const [selectedArea, setSelectedArea] = useState<string>("Todas as Áreas");

  const typeRatio = selectedTypes.length / ALL_TYPES.length;
  const areaAll = selectedArea === "Todas as Áreas";

  const yearData = useMemo(() => {
    return yearDataRaw
      .filter((d) => d.year >= yearRange.from && d.year <= yearRange.to)
      .map((d) => {
        const scale = typeRatio;
        const row: YearRow = {
          year: d.year,
          a1: areaAll || selectedArea === "Área 1" ? Math.round(d.a1 * scale) : 0,
          a2: areaAll || selectedArea === "Área 2" ? Math.round(d.a2 * scale) : 0,
          a3: areaAll || selectedArea === "Área 3" ? Math.round(d.a3 * scale) : 0,
          outras: areaAll ? Math.round(d.outras * scale) : 0,
        };
        return row;
      });
  }, [yearRange, typeRatio, areaAll, selectedArea]);

  const researcherBars = useMemo(() => {
    return researcherBarsRaw.filter(
      (r) =>
        selectedTypes.includes(r.type) && (areaAll || r.area === selectedArea),
    );
  }, [selectedTypes, areaAll, selectedArea]);

  const areaData = useMemo(() => {
    const filtered = areaDataRaw.filter(
      (a) => areaAll || a.label === selectedArea,
    );
    const total = filtered.reduce((s, a) => s + a.value, 0) || 1;
    return filtered.map((a) => ({ ...a, value: Math.round((a.value / total) * 100) }));
  }, [areaAll, selectedArea]);

  const maxBar = Math.max(1, ...researcherBars.map((r) => r.value));
  const maxYear = Math.max(
    1,
    ...yearData.map((d) => d.a1 + d.a2 + d.a3 + d.outras),
  );

  let cumulative = 0;
  const donutSegments = areaData.map((d) => {
    const start = cumulative;
    cumulative += d.value;
    return { ...d, start, end: cumulative };
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
      />
      <main className="ml-[200px] mr-[250px] px-8 py-8">
        {/* Top stats */}
        <section className="grid grid-cols-3 gap-4">
          {[
            { label: "ÁREAS DE PESQUISA", value: String(areaData.length) },
            { label: "PESQUISADORES", value: String(researcherBars.length) },
            {
              label: "PUBLICAÇÕES",
              value: yearData
                .reduce((s, d) => s + d.a1 + d.a2 + d.a3 + d.outras, 0)
                .toLocaleString("pt-BR"),
            },
          ].map((s) => (
            <div key={s.label} className="rounded-xl border border-border bg-card px-5 py-4">
              <p className="text-[10px] font-semibold tracking-wider text-muted-foreground">
                {s.label}
              </p>
              <p className="mt-1 font-serif text-3xl text-primary">{s.value}</p>
            </div>
          ))}
        </section>

        {/* Produções por pesquisador */}
        <section className="mt-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Produções por pesquisador</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="space-y-3">
            {researcherBars.map((b) => (
              <div key={b.name} className="flex items-center gap-3 text-sm">
                <span className="w-32 shrink-0 text-muted-foreground">{b.name}</span>
                <div className="relative h-5 flex-1 overflow-hidden rounded bg-secondary">
                  <div
                    className="h-full rounded bg-primary"
                    style={{ width: `${(b.value / maxBar) * 100}%` }}
                  />
                </div>
                <span className="w-10 text-right text-xs text-foreground">{b.value}</span>
              </div>
            ))}
            {researcherBars.length === 0 && (
              <p className="text-xs text-muted-foreground">Nenhum resultado para os filtros atuais.</p>
            )}
          </div>
        </section>

        {/* Produções por área */}
        <section className="mt-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Produções por área</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="flex items-center gap-8">
            <Donut segments={donutSegments} />
            <div className="flex-1 space-y-2">
              {donutSegments.map((s) => (
                <div key={s.label} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-foreground">
                    <span
                      className="h-3 w-3 rounded-sm"
                      style={{ background: s.color }}
                    />
                    {s.label}
                  </span>
                  <span className="text-muted-foreground">{s.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Produções por ano */}
        <section className="mt-6 rounded-xl border border-border bg-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Produções por ano</h3>
            <button className="text-muted-foreground hover:text-primary">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
          <div className="mb-3 flex flex-wrap gap-3 text-xs">
            {[
              { l: "Área 1", c: "var(--chart-1)" },
              { l: "Área 2", c: "var(--chart-2)" },
              { l: "Área 3", c: "var(--chart-3)" },
              { l: "Outras (9)", c: "var(--chart-4)" },
            ].map((x) => (
              <span key={x.l} className="flex items-center gap-1.5 text-foreground">
                <span className="h-3 w-3 rounded-sm" style={{ background: x.c }} />
                {x.l}
              </span>
            ))}
          </div>
          <div className="flex h-64 items-end gap-3 border-l border-b border-border pl-2 pb-2 pt-2">
            {yearData.map((d) => {
              const total = d.a1 + d.a2 + d.a3 + d.outras;
              const h = total > 0 ? (total / maxYear) * 100 : 0;
              return (
                <div key={d.year} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="flex w-full flex-col-reverse overflow-hidden rounded-t"
                    style={{ height: `${h}%` }}
                  >
                    {total > 0 && (
                      <>
                        <div style={{ height: `${(d.a1 / total) * 100}%`, background: "var(--chart-1)" }} />
                        <div style={{ height: `${(d.a2 / total) * 100}%`, background: "var(--chart-2)" }} />
                        <div style={{ height: `${(d.a3 / total) * 100}%`, background: "var(--chart-3)" }} />
                        <div style={{ height: `${(d.outras / total) * 100}%`, background: "var(--chart-4)" }} />
                      </>
                    )}
                  </div>
                  <span className="text-[10px] text-muted-foreground">{d.year}</span>
                </div>
              );
            })}
          </div>
        </section>

        <div className="mt-6 flex items-center gap-3">
          <Link
            to="/"
            className="rounded-md border border-border bg-secondary px-4 py-2 text-sm text-foreground hover:border-primary"
          >
            ← Voltar ao Início
          </Link>
          <button className="flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary hover:bg-primary/20">
            <Download className="h-4 w-4" /> Exportar relatório
          </button>
        </div>

        <footer className="mt-10 flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground">
          <span>© 2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">Termos de uso</a>
        </footer>
      </main>
    </div>
  );
}

function Donut({
  segments,
}: {
  segments: { label: string; value: number; color: string; start: number; end: number }[];
}) {
  const r = 60;
  const c = 2 * Math.PI * r;
  return (
    <svg width="160" height="160" viewBox="0 0 160 160" className="shrink-0">
      <g transform="translate(80 80) rotate(-90)">
        <circle r={r} fill="none" stroke="var(--secondary)" strokeWidth="22" />
        {segments.map((s) => {
          const dash = ((s.end - s.start) / 100) * c;
          const offset = (s.start / 100) * c;
          return (
            <circle
              key={s.label}
              r={r}
              fill="none"
              stroke={s.color}
              strokeWidth="22"
              strokeDasharray={`${dash} ${c - dash}`}
              strokeDashoffset={-offset}
            />
          );
        })}
      </g>
    </svg>
  );
}
