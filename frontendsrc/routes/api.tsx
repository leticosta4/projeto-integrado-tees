import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api")({
  head: () => ({
    meta: [{ title: "API — Lattes" }],
  }),
  component: ApiDocs,
});

function ApiDocs() {
  const swaggerUrl = `${"http://localhost:5000"}/api/docs`;

  return (
    <div className="ml-[200px] min-h-screen bg-background">
      <header className="border-b border-border px-6 py-4">
        <h1 className="font-serif text-xl text-foreground">
          Documentação da <span className="text-primary">API</span>
        </h1>
      </header>
      <iframe
        src={swaggerUrl}
        className="h-[calc(100vh-57px)] w-full border-none"
        title="Swagger API Docs"
      />
    </div>
  );
}