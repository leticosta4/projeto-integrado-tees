import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Presentation } from "lucide-react";
import { getConferencePaper, getResearcher, type ConferencePaper, type Researcher } from "@/lib/api";

export const Route = createFileRoute("/publicacao/conference-paper/$id")({
  head: ({ params }) => ({
    meta: [{ title: `Conference Paper ${params.id} - Lattes` }],
  }),
  loader: async ({ params }) => {
    try {
      const conferencePaper = await getConferencePaper(params.id);
      const researcher = await getResearcher(conferencePaper.researcher_id);
      return { conferencePaper, researcher };
    } catch {
      throw notFound();
    }
  },
  component: ConferencePaperPage,
  notFoundComponent: () => (
    <div className="flex min-h-screen items-center justify-center text-foreground">
      Publicacao nao encontrada.
    </div>
  ),
});

function Field({ label, value }: { label: string; value: string | number | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 text-sm text-foreground">{value}</dd>
    </div>
  );
}

function ConferencePaperPage() {
  const { conferencePaper, researcher } = Route.useLoaderData() as {
    conferencePaper: ConferencePaper;
    researcher: Researcher;
  };

  return (
    <div className="min-h-screen bg-background ml-[200px]">
      <header className="border-b border-border bg-sidebar/60 px-6 py-4">
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

      <main className="mx-auto max-w-4xl px-6 py-8">
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
              <Presentation className="h-7 w-7 text-primary" />
            </div>
            <div className="flex-1">
              <span className="rounded-full bg-primary/15 px-2.5 py-0.5 text-xs text-primary">
                Conference Paper
              </span>
              <h1 className="mt-2 font-serif text-2xl text-foreground">{conferencePaper.title}</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Pesquisador:{" "}
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
            <Field label="Ano" value={conferencePaper.year} />
            <Field label="Idioma" value={conferencePaper.language} />
            <Field label="Natureza" value={conferencePaper.nature} />
            <Field label="Pais" value={conferencePaper.country} />
            <Field label="Evento" value={conferencePaper.event_name} />
            <Field label="Cidade do Evento" value={conferencePaper.event_city} />
            <Field label="Ano do Evento" value={conferencePaper.event_year} />
            <Field label="Classificacao do Evento" value={conferencePaper.event_classification} />
            <Field label="Anais" value={conferencePaper.proceedings_title} />
            <Field label="ISBN" value={conferencePaper.isbn} />
            <Field label="Paginas" value={
              conferencePaper.first_page && conferencePaper.last_page
                ? `${conferencePaper.first_page} - ${conferencePaper.last_page}`
                : conferencePaper.first_page ?? conferencePaper.last_page
            } />
            <Field label="DOI" value={conferencePaper.doi} />
          </dl>

          {conferencePaper.doi && (
            <div className="mt-6 border-t border-border pt-6">
              <a
                href={`https://doi.org/${conferencePaper.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Acessar publicacao via DOI
              </a>
            </div>
          )}
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