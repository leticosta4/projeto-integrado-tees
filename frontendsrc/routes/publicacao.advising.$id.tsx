import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, GraduationCap, Search } from "lucide-react";
import { getAdvising, getResearcher, type Advising, type Researcher } from "@/lib/api";

export const Route = createFileRoute("/publicacao/advising/$id")({
  validateSearch: (search: Record<string, unknown>) => ({
    from: typeof search.from === "string" ? search.from : "",
  }),
  head: ({ params }) => ({
    meta: [{ title: `Orientacao ${params.id} - Lattes` }],
  }),
  loader: async ({ params }) => {
    try {
      const advising = await getAdvising(params.id);
      const researcher = await getResearcher(advising.researcher_id);
      return { advising, researcher };
    } catch {
      throw notFound();
    }
  },
  component: AdvisingPage,
  notFoundComponent: () => (
    <div className="flex min-h-screen items-center justify-center text-foreground">
      Orientacao nao encontrada.
    </div>
  ),
});

function Field({ label, value }: { label: string; value: string | number | boolean | null | undefined }) {
  if (value === null || value === undefined || value === "") return null;
  const display = typeof value === "boolean" ? (value ? "Sim" : "Nao") : value;
  return (
    <div>
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 text-sm text-foreground">{display}</dd>
    </div>
  );
}

function AdvisingPage() {
  const { advising, researcher } = Route.useLoaderData() as {
    advising: Advising;
    researcher: Researcher;
  };
  const { from } = Route.useSearch();

  return (
    <div className="min-h-screen bg-background ml-[200px]">
      {from !== "search" && (
        <header className="border-b border-border/80 bg-card/80 px-6 py-4 backdrop-blur">
          <div className="mx-auto flex max-w-4xl items-center gap-4">
            <Link
              to="/pesquisador/$id"
              params={{ id: String(researcher.id) }}
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar para {researcher.full_name}
            </Link>
          </div>
        </header>
      )}

      <main className="mx-auto max-w-4xl px-6 py-8">
        <div className="rounded-xl border border-border/80 bg-card p-6 shadow-[var(--shadow-card)]">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
              <GraduationCap className="h-7 w-7 text-primary" />
            </div>
            <div className="flex-1">
              <span className="rounded-full bg-primary/15 px-2.5 py-0.5 text-xs text-primary">
                Orientacao
              </span>
              <h1 className="mt-2 font-serif text-2xl text-foreground">{advising.title}</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Orientador:{" "}
                <Link
                  to="/pesquisador/$id"
                  params={{ id: String(researcher.id) }}
                  className="text-primary hover:underline"
                >
                  {researcher.full_name}
                </Link>
              </p>
            </div>
          </div>

          <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-border pt-6 md:grid-cols-3">
            <Field label="Ano" value={advising.year} />
            <Field label="Nivel" value={advising.level} />
            <Field label="Tipo" value={advising.advising_type} />
            <Field label="Orientando" value={advising.advisee_name} />
            <Field label="Instituicao" value={advising.institution} />
            <Field label="Curso" value={advising.course} />
            <Field label="Pais" value={advising.country} />
            <Field label="Bolsista" value={advising.had_scholarship} />
            <Field label="Agencia de Fomento" value={advising.funding_agency} />
          </dl>

          <div className="mt-6 flex items-center justify-end border-t border-border pt-6">
            <button
              onClick={() => window.history.back()}
              className="flex items-center gap-1.5 rounded-md border border-border bg-secondary px-4 py-2 text-sm text-foreground hover:border-primary hover:text-primary"
            >
              <Search className="h-4 w-4" />
              Voltar para busca
            </button>
          </div>
        </div>
      </main>

      <footer className="border-t border-border px-6 py-4 text-xs text-muted-foreground">
        <div className="mx-auto flex max-w-4xl items-center justify-between">
          <span>2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">Termos de uso</a>
        </div>
      </footer>
    </div>
  );
}