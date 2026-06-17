import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useState } from "react";
import { BarChart3, Download, User } from "lucide-react";
import { FiltrosPanel } from "@/components/FiltrosPanel";
import {
  getResearcher,
  listPapers,
  listResearchAreas,
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
      const [researcher, papers, areas] = await Promise.all([
        getResearcher(params.id),
        listPapers({ researcher_id: params.id }),
        listResearchAreas({ researcher_id: params.id }),
      ]);
      return { researcher, papers, areas };
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
  return area.specialty ?? area.sub_area ?? area.area ?? area.major_area ?? "Area nao informada";
}

function researcherDescription(researcher: Researcher) {
  const parts = [
    researcher.citation_name ? `Nome em citacoes: ${researcher.citation_name}` : null,
    researcher.nationality ? `Nacionalidade: ${researcher.nationality}` : null,
    researcher.birth_state ? `UF de nascimento: ${researcher.birth_state}` : null,
    researcher.update_date ? `Curriculo atualizado em ${researcher.update_date}` : null,
  ].filter(Boolean);

  return parts.length > 0
    ? parts.join(" - ")
    : "Pesquisador importado a partir dos dados do Curriculo Lattes.";
}

function ResearcherProfile() {
  const { researcher, papers, areas } = Route.useLoaderData() as {
    researcher: Researcher;
    papers: Paper[];
    areas: ResearchArea[];
  };
  const [filtersOpen, setFiltersOpen] = useState(true);

  return (
    <div className="min-h-screen bg-background">
      <FiltrosPanel isOpen={filtersOpen} onToggle={() => setFiltersOpen((value) => !value)} />
      <main className={`ml-[200px] ${filtersOpen ? "mr-[250px]" : "mr-[40px]"} px-8 py-8`}>
        <section className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-start gap-5">
            <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
              <User className="h-10 w-10 text-primary" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="font-serif text-2xl text-foreground">{researcher.full_name}</h1>
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
            Publicacoes
          </h2>
          <p className="mt-1 font-serif text-5xl text-foreground">{papers.length}</p>
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
              <span className="text-sm text-muted-foreground">Nenhuma area cadastrada.</span>
            )}
          </div>
        </section>

        <section className="mt-8 rounded-xl border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-foreground">Producoes Cientificas</h2>
            <button className="flex items-center gap-1.5 rounded-md border border-border bg-secondary px-3 py-1.5 text-xs text-foreground hover:border-primary">
              <Download className="h-3.5 w-3.5" /> Exportar CSV
            </button>
          </div>
          <div className="divide-y divide-border">
            {papers.slice(0, 20).map((paper) => (
              <div key={paper.id} className="flex items-center gap-4 py-3 text-sm">
                <span className="w-12 shrink-0 text-muted-foreground">
                  {paper.year ?? "-"}
                </span>
                <span className="w-24 shrink-0 rounded bg-secondary px-2 py-0.5 text-center text-xs text-foreground">
                  Paper
                </span>
                <span className="flex-1 text-foreground/90">{paper.title}</span>
                <span className="text-xs text-primary">{paper.journal ?? paper.nature ?? ""}</span>
              </div>
            ))}
            {papers.length === 0 && (
              <p className="py-6 text-sm text-muted-foreground">
                Nenhuma publicacao cadastrada para este pesquisador.
              </p>
            )}
          </div>
          {papers.length > 20 && (
            <button className="mt-4 text-xs text-muted-foreground hover:text-primary">
              Exibindo 20 de {papers.length} itens
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
