import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Search, SlidersHorizontal, User } from "lucide-react";
import { researchers } from "@/lib/mock-data";

export const Route = createFileRoute("/")({
  validateSearch: (search: Record<string, unknown>) => ({
    q: typeof search.q === "string" ? search.q : "",
  }),
  head: () => ({
    meta: [
      { title: "Portal de Pesquisa Lattes" },
      { name: "description", content: "Busca de pesquisadores e produções científicas." },
    ],
  }),
  component: Home,
});

function Home() {
  const { q: committedQuery } = Route.useSearch();
  const [query, setQuery] = useState(committedQuery);
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();
  const hasQuery = committedQuery.trim().length > 0;

  const handleSearch = () => {
    navigate({ to: "/", search: { q: query }, replace: true });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const results = hasQuery
    ? researchers.filter(
        (r) =>
          r.name.toLowerCase().includes(committedQuery.toLowerCase()) ||
          r.areas.some((a) => a.toLowerCase().includes(committedQuery.toLowerCase())),
      )
    : [];

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
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" onClick={handleSearch} />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Título genérico sendo pesquisado"
                  className="w-full rounded-full border border-border bg-input py-2 pl-10 pr-4 text-sm text-foreground focus:border-primary focus:outline-none"
                />
              </div>
              <button className="rounded-md border border-border bg-secondary px-3 py-2 text-xs text-foreground hover:border-primary">
                Relevância
              </button>
              <button className="rounded-md border border-border bg-secondary px-3 py-2 text-xs text-foreground hover:border-primary">
                Data
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
                placeholder="Buscar pesquisador, área ou publicação..."
                className="w-full rounded-full border border-border bg-input py-3 pl-5 pr-12 text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
              />
              <Search className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" onClick={handleSearch} />
            </div>
            <button
              onClick={() => setShowFilters((v) => !v)}
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
                      placeholder="Até"
                      className="w-full rounded-md border border-border bg-input px-2 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-xs font-medium text-muted-foreground">
                    Tipo de Publicação
                  </label>
                  <div className="grid grid-cols-2 gap-1.5 text-sm">
                    {["Paper", "Conference Paper", "Advising"].map((t) => (
                      <label key={t} className="flex items-center gap-2 text-foreground/90">
                        <input
                          type="checkbox"
                          defaultChecked
                          className="h-3.5 w-3.5 accent-[var(--teal)]"
                        />
                        {t}
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
        </section>
      ) : (
        <section className="mx-auto max-w-6xl px-6 py-8">
          <p className="mb-4 text-sm text-muted-foreground">
            {results.length} pesquisador{results.length !== 1 ? "es" : ""} encontrado
            {results.length !== 1 ? "s" : ""}
          </p>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {results.map((r) => (
              <button
                key={r.id}
                onClick={() => navigate({ to: "/pesquisador/$id", params: { id: r.id } })}
                className="group flex items-start gap-4 rounded-xl border border-border bg-card p-5 text-left transition-all hover:border-primary hover:shadow-[0_0_0_1px_var(--teal)]"
              >
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/15 ring-2 ring-primary/40">
                  <User className="h-7 w-7 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-foreground group-hover:text-primary">
                    {r.name}
                  </h3>
                  <p className="mt-0.5 text-xs text-muted-foreground">{r.institution}</p>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {r.areas.slice(0, 3).map((a) => (
                      <span
                        key={a}
                        className="rounded-full bg-primary/15 px-2 py-0.5 text-[11px] text-primary"
                      >
                        {a}
                      </span>
                    ))}
                  </div>
                  <p className="mt-3 text-xs font-medium text-foreground">
                    {r.publications} publicações
                  </p>
                </div>
              </button>
            ))}
          </div>
        </section>
      )}

      <footer className="border-t border-border px-6 py-4 text-xs text-muted-foreground">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <span>© 2024 Universidade do Estado da Bahia - UNEB</span>
          <a href="#" className="hover:text-primary">
            Termos de uso
          </a>
        </div>
      </footer>
    </div>
  );
}
