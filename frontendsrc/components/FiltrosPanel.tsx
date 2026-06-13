import { Link } from "@tanstack/react-router";
import { Menu, ArrowLeft, Download, ChevronRight, ChevronLeft } from "lucide-react";

const PUB_TYPES = ["Paper", "Conference Paper", "Advising"] as const;
const AREA_OPTIONS = ["Todas as Áreas", "Área 1", "Área 2", "Área 3"] as const;

export function FiltrosPanel({
  showExport = false,
  isOpen = true,
  onToggle,
  yearRange,
  onYearRangeChange,
  selectedTypes,
  onTypesChange,
  selectedArea,
  onAreaChange,
}: {
  showExport?: boolean;
  isOpen?: boolean;
  onToggle?: () => void;
  yearRange?: { from: number; to: number };
  onYearRangeChange?: (r: { from: number; to: number }) => void;
  selectedTypes?: string[];
  onTypesChange?: (t: string[]) => void;
  selectedArea?: string;
  onAreaChange?: (a: string) => void;
}) {
  if (!isOpen) {
    return (
      <aside className="fixed right-0 top-0 z-20 flex h-screen w-[40px] flex-col items-center gap-3 border-l border-border bg-sidebar py-4">
        <button
          onClick={onToggle}
          aria-label="Abrir filtros"
          className="rounded-md p-1 text-primary hover:bg-primary/10"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div
          className="mt-2 flex items-center gap-1 text-xs font-semibold tracking-[0.25em] text-foreground"
          style={{ writingMode: "vertical-rl" }}
        >
          <Menu className="h-3.5 w-3.5 text-primary" />
          FILTROS
        </div>
      </aside>
    );
  }

  const from = yearRange?.from ?? 2018;
  const to = yearRange?.to ?? 2024;
  const types = selectedTypes ?? [...PUB_TYPES];
  const area = selectedArea ?? AREA_OPTIONS[0];

  const toggleType = (t: string) => {
    if (!onTypesChange) return;
    onTypesChange(types.includes(t) ? types.filter((x) => x !== t) : [...types, t]);
  };

  return (
    <aside className="fixed right-0 top-0 z-20 flex h-screen w-[250px] flex-col gap-5 overflow-y-auto border-l border-border bg-sidebar px-4 py-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold tracking-wide text-foreground">
          <Menu className="h-4 w-4 text-primary" />
          FILTROS
        </div>
        {onToggle && (
          <button
            onClick={onToggle}
            aria-label="Recolher filtros"
            className="rounded-md p-1 text-primary hover:bg-primary/10"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        )}
      </div>

      <div>
        <label className="mb-2 block text-xs font-medium text-muted-foreground">
          Intervalo de Anos
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            value={from}
            onChange={(e) =>
              onYearRangeChange?.({ from: Number(e.target.value) || 0, to })
            }
            className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
          />
          <input
            type="number"
            value={to}
            onChange={(e) =>
              onYearRangeChange?.({ from, to: Number(e.target.value) || 0 })
            }
            className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
          />
        </div>
      </div>

      <div>
        <label className="mb-2 block text-xs font-medium text-muted-foreground">
          Tipo de Publicação
        </label>
        <div className="space-y-1.5 text-sm">
          {PUB_TYPES.map((t) => (
            <label key={t} className="flex items-center gap-2 text-foreground/90">
              <input
                type="checkbox"
                checked={types.includes(t)}
                onChange={() => toggleType(t)}
                className="h-3.5 w-3.5 accent-[var(--teal)]"
              />
              {t}
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="mb-2 block text-xs font-medium text-muted-foreground">
          Área de Pesquisa
        </label>
        <select
          value={area}
          onChange={(e) => onAreaChange?.(e.target.value)}
          className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
        >
          {AREA_OPTIONS.map((a) => (
            <option key={a}>{a}</option>
          ))}
        </select>
      </div>

      {showExport && (
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-foreground">
            <Download className="h-3.5 w-3.5" />
            Exportar Dados
          </div>
          <div className="space-y-2">
            <button className="flex w-full items-center justify-between rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground hover:border-primary">
              Por Pesquisador <span className="text-primary">CSV</span>
            </button>
            <button className="flex w-full items-center justify-between rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground hover:border-primary">
              Por Área <span className="text-primary">CSV</span>
            </button>
          </div>
        </div>
      )}

      <Link
        to="/"
        className="mt-auto flex items-center justify-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar ao Início
      </Link>
    </aside>
  );
}
