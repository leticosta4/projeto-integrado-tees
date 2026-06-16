const API_URL = "http://localhost:3000";

export async function fetchResearchers(params?: Record<string, string>) {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  const res = await fetch(`${API_URL}/researchers${qs}`);
  if (!res.ok) throw new Error("Erro ao buscar pesquisadores");
  return res.json();
}

export async function fetchResearcher(id: string) {
  const res = await fetch(`${API_URL}/researchers/${id}`);
  if (!res.ok) throw new Error("Pesquisador não encontrado");
  return res.json();
}


//falta add funções similares para as outras entidades