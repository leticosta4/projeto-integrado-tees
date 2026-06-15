import { Link, useRouterState } from "@tanstack/react-router";
import { Home, BarChart3, Code2 } from "lucide-react";

export function Sidebar() {
  const { location } = useRouterState();
  const path = location.pathname;

  const items = [
    { to: "/", label: "Início", icon: Home, match: path === "/" },
    { to: "/modulo-analitico", label: "Módulo Analítico", icon: BarChart3, match: path.startsWith("/modulo") },
    { to: "/api", label: "API", icon: Code2, match: path.startsWith("/api") },
  ];

  return (
    <aside className="fixed left-0 top-0 z-20 flex h-screen w-[200px] flex-col border-r border-border bg-sidebar px-4 py-6">
      <div className="mb-8 px-2">
        <h2 className="font-serif text-lg leading-tight text-foreground">
          Pesquisas
          <br />
          <span className="text-primary">Lattes</span>
        </h2>
      </div>
      <nav className="flex flex-col gap-1">
        {items.map((it) => {
          const Icon = it.icon;
          return (
            <Link
              key={it.to}
              to={it.to}
              className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                it.match
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4" />
              {it.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
