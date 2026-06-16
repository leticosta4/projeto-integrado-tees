export type Researcher = {
  id: string;
  name: string;
  institution: string;
  areas: string[];
  publications: number;
  citations: number;
  hIndex: number;
  email?: string;
  lattes?: string;
  bio: string;
};

export type Publication = {
  id: string;
  researcherId: string;
  title: string;
  type: "Paper" | "Conference Paper" | "Advising";
  year: number;
  area: string;
  citations: number;
};

export const researchers: Researcher[] = [
  {
    id: "1",
    name: "Ana Carolina Souza",
    institution: "Universidade do Estado da Bahia - UNEB",
    areas: ["Engenharia de Software", "Sistemas de Informacao", "Busca Semantica"],
    publications: 42,
    citations: 318,
    hIndex: 11,
    email: "ana.souza@uneb.br",
    lattes: "http://lattes.cnpq.br/0000000000000001",
    bio: "Pesquisadora com atuacao em engenharia de software, recuperacao de informacao e sistemas academicos.",
  },
  {
    id: "2",
    name: "Bruno Almeida Santos",
    institution: "Universidade Federal da Bahia - UFBA",
    areas: ["Inteligencia Artificial", "Mineracao de Dados", "Aprendizado de Maquina"],
    publications: 37,
    citations: 284,
    hIndex: 9,
    email: "bruno.santos@ufba.br",
    lattes: "http://lattes.cnpq.br/0000000000000002",
    bio: "Atua em modelos de aprendizado de maquina aplicados a dados cientificos e educacionais.",
  },
  {
    id: "3",
    name: "Camila Rocha Lima",
    institution: "Instituto Federal da Bahia - IFBA",
    areas: ["Banco de Dados", "Visualizacao de Dados", "Analise Bibliometrica"],
    publications: 29,
    citations: 197,
    hIndex: 7,
    email: "camila.lima@ifba.edu.br",
    lattes: "http://lattes.cnpq.br/0000000000000003",
    bio: "Desenvolve pesquisas em organizacao de dados, dashboards analiticos e metricas de producao cientifica.",
  },
];

export const publications: Publication[] = [
  {
    id: "p1",
    researcherId: "1",
    title: "Sistema de busca hibrida para curriculos academicos",
    type: "Paper",
    year: 2024,
    area: "Engenharia de Software",
    citations: 18,
  },
  {
    id: "p2",
    researcherId: "1",
    title: "Indexacao semantica de producoes cientificas",
    type: "Conference Paper",
    year: 2023,
    area: "Busca Semantica",
    citations: 11,
  },
  {
    id: "p3",
    researcherId: "2",
    title: "Classificacao automatica de pesquisadores por area",
    type: "Paper",
    year: 2024,
    area: "Inteligencia Artificial",
    citations: 21,
  },
  {
    id: "p4",
    researcherId: "3",
    title: "Dashboards para acompanhamento de producao academica",
    type: "Advising",
    year: 2022,
    area: "Visualizacao de Dados",
    citations: 6,
  },
];

export function getResearcher(id: string) {
  return researchers.find((researcher) => researcher.id === id);
}
