import { createFileRoute, notFound, Link } from "@tanstack/react-router";
import { useState } from "react";
import { User, Download, BarChart3 } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";
import { getResearcher, publications, type Researcher } from "@/lib/mock-data";

export const Route = createFileRoute("/pesquisador/$id")({
  head: ({ params }) => ({
    meta: [{ title: `Pesquisador ${params.id} — Lattes` }],
  }),
  loader: ({ params }) => {
    const r = getResearcher(params.id);
    if (!r) throw notFound();
    return { researcher: r as NonNullable<ReturnType<typeof getResearcher>> };
  },
  component: ResearcherProfile,
  notFoundComponent: () => (
    <div className="flex min-h-screen items-center justify-center text-foreground">
      Pesquisador não encontrado.
    </div>
  ),
  errorComponent: ({ error }) => (
    <div className="flex min-h-screen items-center justify-center text-destructive">
      {error.message}
    </div>
  ),
});

function ResearcherProfile() {
  const { researcher } = Route.useLoaderData() as { researcher: Researcher };
  const [filtersOpen, setFiltersOpen] = useState(true);

  return (
    <div className="min-h-screen bg-background">
      <FiltrosPanel isOpen={filtersOpen} onToggle={() => setFiltersOpen((v) => !v)} />
      <main className={`ml-[200px] ${filtersOpen ? "mr-[250px]" : "mr-[40px]"} px-8 py-8`}>
        {/* Profile card */}
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-start gap-5">
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
              <User className="h-10 w-10 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="font-serif text-2xl text-foreground">{researcher.name}</h1>
                <span className="rounded-full bg-primary/15 px-2.5 py-0.5 text-xs text-primary">
                  Pesquisador
                </span>
              </div>
              <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
                {researcher.description}
              </p>
              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                <span>ID Lattes: {researcher.lattesId}</span>
                <button className="rounded-md border border-border bg-secondary px-2 py-1 text-foreground hover:border-primary">
                  Ver Lattes
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Publicações count */}
        <section className="mt-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Publicações
          </h2>
          <p className="mt-1 font-serif text-5xl text-foreground">{researcher.publications}</p>
        </section>

        {/* Áreas de atuação */}
        <section className="mt-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Áreas de Atuação
          </h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {researcher.areas.map((a) => (
              <span
                key={a}
                className="rounded-full border border-primary/40 bg-primary/10 px-3 py-1 text-sm text-primary"
              >
                {a}
              </span>
            ))}
          </div>
        </section>

        {/* Produções */}
        <section className="mt-8 rounded-xl border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-foreground">Produções Científicas</h2>
            <button className="flex items-center gap-1.5 rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground hover:border-primary">
              <Download className="h-3.5 w-3.5" /> Exportar CSV
            </button>
          </div>
          <div className="divide-y divide-border">
            {publications.map((p, i) => (
              <div key={i} className="flex items-center gap-4 py-3 text-sm">
                <span className="w-12 shrink-0 text-muted-foreground">{p.year}</span>
                <span className="w-24 shrink-0 rounded bg-secondary px-2 py-0.5 text-center text-xs text-foreground">
                  {p.type}
                </span>
                <span className="flex-1 text-foreground/90">{p.title}</span>
                <span className="text-xs text-primary">{p.area}</span>
              </div>
            ))}
          </div>
          <button className="mt-4 text-xs text-muted-foreground hover:text-primary">
            Ver lista completa ({researcher.publications} itens)
          </button>
        </section>

        {/* Módulo Analítico link */}
        <section className="mt-8">
          <Link
            to="/modulo-analitico"
            className="inline-flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/20"
          >
            <BarChart3 className="h-4 w-4" />
            Abrir Módulo Analítico
          </Link>
        </section>

        <footer className="mt-10 flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground">
          <span>© 2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">Termos de uso</a>
        </footer>
      </main>
    </div>
  );
}
