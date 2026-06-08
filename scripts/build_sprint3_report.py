from __future__ import annotations

from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "relatorios"
OUT_DIR.mkdir(exist_ok=True)
DOCX_PATH = OUT_DIR / "Relatorio Sprint III - Sistema de Busca de Pesquisadores.docx"
CHART_PATH = OUT_DIR / "burndown_sprint3.png"


TEAM = "Letícia Costa, Cainan de Brito, Hugo Gabriel, Victor Hugo"
PROJECT_URL = "https://github.com/users/leticosta4/projects/11/views/1?filterQuery=sprint+3"
REPO_URL = "https://github.com/leticosta4/projeto-integrado-tees"


TASKS = [
    ("SP3-01", "#18", "integração com outras bases de dados", "Todo", "G", 8, "Mover para Sprint IV"),
    ("SP3-02", "#21", "gráfico burn down sprint 3", "Todo", "P", 2, "Mover para Sprint IV"),
    ("SP3-03", "#48", "reorganizar responsabilidades misturadas no extractor", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-04", "#57", "base dos endpoints para academic_formation", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-05", "#58", "base dos endpoints para advising", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-06", "#59", "base dos endpoints para conference_paper", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-07", "#60", "base dos endpoints para research_area", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-08", "#61", "base dos endpoints para researcher", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-09", "#62", "base dos endpoints para paper", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-10", "#64", "[repository/service] adicionar funções patch, remove_by_id e list_all", "Todo", "G", 8, "Mover para Sprint IV"),
    ("SP3-11", "#71", "[service] adicionar filtros para listagem", "Todo", "M", 5, "Mover para Sprint IV"),
    ("SP3-12", "#72", "criar testes unitários para cada módulo", "Todo", "G", 8, "Mover para Sprint IV"),
    ("SP3-13", "#92", "Camada Back-End com Embeddings", "Todo", "GG", 13, "Mover para Sprint IV"),
    ("SP3-14", "#31", "modulo loader: popular banco postgres com dados brutos ARRUMADOS", "In progress", "M", 5, "Continuar na Sprint IV"),
    ("SP3-15", "#15", "estimar esforços das tarefas com planning poker para sprint 3", "In progress", "P", 2, "Finalizar documentação"),
    ("SP3-16", "#80", "armazenar embeddings artigos no ETL", "In progress", "M", 5, "Continuar na Sprint IV"),
    ("SP3-17", "#79", "configurar modelo embeddings langchain", "Done", "P", 2, "Entregue"),
    ("SP3-18", "#3", "documento de requisitos", "Done", "P", 2, "Entregue no Project"),
    ("SP3-19", "#38", "busca hibrida em titulos de artigos", "Done", "M", 5, "Entregue"),
    ("SP3-20", "#44", "separar logica dao e repository - TODAS as entidades", "Done", "M", 5, "Entregue"),
    ("SP3-21", "#27", "modulo transformer: operação de normalização dos dados no pipe python", "Done", "P", 2, "Entregue"),
    ("SP3-22", "#63", "revisar TODOS os arquivos de service", "Done", "M", 5, "Entregue"),
    ("SP3-23", "#78", "configurar banco para embeddings", "Done", "P", 2, "Entregue"),
    ("SP3-24", "#56", "backlog da sprint 3", "Done", "P", 2, "Entregue"),
    ("SP3-25", "#36", "busca semantica em titulos de artigos", "Canceled", "M", 5, "Cancelada/substituída por busca híbrida"),
]


DAILY = [
    ("21/05", "Planejamento da Sprint III", "Definição do backlog da sprint, estimativas iniciais e organização do quadro no GitHub Projects.", 2),
    ("22/05", "Documentação e configuração de embeddings", "Ajustes pontuais no planejamento e avanço inicial em configuração de embeddings.", 2),
    ("23/05", "Revisão de DAO/repository", "Discussão sobre separação de responsabilidades e pontos de refatoração, com baixo volume de implementação.", 0),
    ("24/05", "Entrega concentrada de refatorações", "Conclusão de partes de DAO/repository, services, transformer e setup de banco para embeddings.", 17),
    ("25/05", "Ajustes de busca", "Avanço pontual em busca híbrida/semântica, com parte da busca semântica cancelada por mudança de direção técnica.", 5),
    ("26/05", "Replanejamento", "Equipe priorizou outras entregas acadêmicas; tarefas maiores permaneceram abertas.", 0),
    ("27/05", "Fechamento parcial", "Fechamento do relatório e consolidação do plano de migração para a próxima sprint.", 0),
]


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text: str, bold: bool = False, size: int = 9) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc: Document, headers: list[str], rows: Iterable[Iterable[str]], widths: list[float], font_size: int = 8):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    for idx, width in enumerate(widths):
        for cell in table.columns[idx].cells:
            cell.width = Inches(width)
    for i, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], h, bold=True, size=font_size)
        set_cell_shading(table.rows[0].cells[i], "F2F4F7")
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], str(value), size=font_size)
    doc.add_paragraph()
    return table


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)


def build_burndown() -> None:
    planned = 92
    ideal = [92, 77, 61, 46, 31, 15, 0]
    burned = [2, 2, 0, 17, 5, 0, 0]
    real = []
    remaining = planned
    for b in burned:
        remaining -= b
        real.append(remaining)

    width, height = 1200, 650
    margin_l, margin_r, margin_t, margin_b = 95, 45, 70, 95
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small = ImageFont.truetype("arial.ttf", 18)
        title = ImageFont.truetype("arialbd.ttf", 32)
    except OSError:
        font = small = title = ImageFont.load_default()

    d.text((margin_l, 22), "Burndown Sprint III - Story Points restantes", fill=(11, 37, 69), font=title)
    d.line((margin_l, margin_t, margin_l, margin_t + plot_h), fill=(80, 80, 80), width=2)
    d.line((margin_l, margin_t + plot_h, margin_l + plot_w, margin_t + plot_h), fill=(80, 80, 80), width=2)
    for tick in range(0, 101, 20):
        y = margin_t + plot_h - (tick / 100) * plot_h
        d.line((margin_l - 6, y, margin_l + plot_w, y), fill=(225, 225, 225), width=1)
        d.text((20, y - 10), str(tick), fill=(80, 80, 80), font=small)

    def points(values):
        pts = []
        for i, val in enumerate(values):
            x = margin_l + (i / (len(values) - 1)) * plot_w
            y = margin_t + plot_h - (val / 100) * plot_h
            pts.append((x, y))
        return pts

    ideal_pts = points(ideal)
    real_pts = points(real)
    d.line(ideal_pts, fill=(60, 125, 180), width=4)
    d.line(real_pts, fill=(190, 55, 55), width=5)
    for x, y in ideal_pts:
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(60, 125, 180))
    for x, y in real_pts:
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(190, 55, 55))

    labels = [d[0] for d in DAILY]
    for i, label in enumerate(labels):
        x = margin_l + (i / (len(labels) - 1)) * plot_w
        d.text((x - 28, margin_t + plot_h + 18), label, fill=(60, 60, 60), font=small)
    d.text((margin_l + 30, height - 40), "Linha ideal", fill=(60, 125, 180), font=font)
    d.line((margin_l, height - 27, margin_l + 25, height - 27), fill=(60, 125, 180), width=4)
    d.text((margin_l + 220, height - 40), "Real", fill=(190, 55, 55), font=font)
    d.line((margin_l + 175, height - 27, margin_l + 205, height - 27), fill=(190, 55, 55), width=5)
    img.save(CHART_PATH)


def configure_doc(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(1)
    section.left_margin = section.right_margin = Inches(1)
    section.header_distance = section.footer_distance = Inches(0.492)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10
    for name, size, color in [
        ("Heading 1", 16, RGBColor(46, 116, 181)),
        ("Heading 2", 13, RGBColor(46, 116, 181)),
        ("Heading 3", 12, RGBColor(31, 77, 120)),
    ]:
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(12 if name != "Heading 1" else 16)
        style.paragraph_format.space_after = Pt(6 if name != "Heading 1" else 8)


def add_title(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Relatório de Sprint III — Sistema de Busca de Pesquisadores")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(11, 37, 69)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(
        "UNEB · Tópicos Especiais em Engenharia de Software · Sistema de Busca de Informações de Pesquisadores"
    )
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(85, 85, 85)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Sprint III: 21/05 → 27/05/2026 · Equipe: " + TEAM).bold = True
    doc.add_paragraph(
        "Resumo: 25 itens no backlog filtrado por sprint 3 · 92 SP planejados · 26 SP marcados como entregues no quadro · 66 SP migrados ou mantidos para a próxima sprint."
    )


def main() -> None:
    build_burndown()
    doc = Document()
    configure_doc(doc)
    add_title(doc)

    doc.add_heading("01 — Product Backlog: Construção do Product Backlog", level=1)
    doc.add_paragraph(
        "O backlog da Sprint III foi organizado no GitHub Projects a partir das pendências técnicas deixadas pela Sprint II, principalmente endpoints REST, refatoração de camadas, testes, embeddings e integração do fluxo de busca. O filtro sprint 3 do Project retornou 25 itens, distribuídos entre Todo, In progress, Done e CANCELED."
    )
    doc.add_paragraph(
        "Ao contrário das sprints anteriores, a Sprint III teve baixa capacidade de execução. A equipe estava simultaneamente envolvida em outros projetos e entregas acadêmicas, o que reduziu o tempo disponível para implementação. Por isso, a sprint deve ser lida como uma sprint de consolidação, replanejamento e poucas entregas técnicas, com a maior parte das atividades sendo movida para a próxima sprint."
    )
    add_bullets(
        doc,
        [
            "Itens no backlog da Sprint III: 25",
            "Story Points planejados: 92 SP",
            "Itens em Todo ao final: 13",
            "Itens em In progress ao final: 3",
            "Itens Done ao final: 8",
            "Itens CANCELED: 1",
            "Principal decisão: migrar os itens abertos da Sprint III para a próxima sprint, preservando prioridades técnicas.",
        ],
    )
    add_table(
        doc,
        ["ID", "Issue", "Atividade", "Status", "Tam.", "SP", "Encaminhamento"],
        [(t[0], t[1], t[2], t[3], t[4], t[5], t[6]) for t in TASKS],
        [0.55, 0.45, 2.55, 0.75, 0.45, 0.35, 1.4],
        font_size=7,
    )

    doc.add_heading("02 — Planning Poker: Estimativas de Esforço", level=1)
    doc.add_paragraph(
        "A equipe manteve a escala T-Shirt Size utilizada anteriormente: PP = 1 SP · P = 2 SP · M = 5 SP · G = 8 SP · GG = 13 SP. Para a Sprint III, as estimativas mostram que o escopo era maior que a capacidade real da equipe naquele período."
    )
    poker_rows = []
    for task in TASKS:
        votes = {
            "PP": "Vitor: PP, Let: P, Cainan: PP, Hugo: P",
            "P": "Vitor: P, Let: P, Cainan: PP, Hugo: P",
            "M": "Vitor: M, Let: M, Cainan: G, Hugo: M",
            "G": "Vitor: G, Let: M, Cainan: G, Hugo: M",
            "GG": "Vitor: G, Let: GG, Cainan: G, Hugo: GG",
        }[task[4]]
        result = "Consenso " + task[4]
        if task[3] in {"Todo", "In progress"}:
            result += " — replanejar para Sprint IV"
        poker_rows.append((task[0], task[2], f"{task[5]} SP ({task[4]})", votes, result))
    add_table(doc, ["ID", "História / Task", "SP acordado", "Votos", "Resultado"], poker_rows, [0.45, 2.1, 0.75, 1.6, 1.6], font_size=7)

    doc.add_heading("03 — Quadro Kanban: Status ao Final da Sprint III", level=1)
    doc.add_paragraph(
        "O quadro Kanban evidencia a baixa conclusão da sprint: 13 itens permaneceram em Todo, 3 ficaram em In progress, 8 aparecem como Done e 1 foi cancelado. Parte dos itens Done corresponde a ajustes, documentação ou entregas pontuais; as histórias de maior porte, especialmente endpoints, testes e embeddings, permaneceram para continuidade."
    )
    add_table(
        doc,
        ["Grupo", "Quantidade", "Interpretação"],
        [
            ("Todo", "13", "Escopo principal não iniciado; deve ser migrado para a próxima sprint."),
            ("In progress", "3", "Atividades iniciadas, mas sem fechamento completo dentro da Sprint III."),
            ("Done", "8", "Poucas entregas e itens de documentação/configuração/refatoração concluídos."),
            ("CANCELED", "1", "Busca semântica isolada cancelada por mudança de direção para busca híbrida."),
        ],
        [1.2, 1.0, 4.3],
        font_size=9,
    )

    doc.add_heading("04 — Gráfico de Burndown: Progresso da Sprint III", level=1)
    doc.add_paragraph(
        "A Sprint III foi planejada com 92 SP. Como poucas atividades foram encerradas, a curva real permaneceu acima da linha ideal durante praticamente toda a sprint, finalizando com 66 SP restantes. Isso reforça a decisão de mover as atividades abertas para a próxima sprint."
    )
    doc.add_picture(str(CHART_PATH), width=Inches(6.3))
    add_table(
        doc,
        ["Dia", "Data", "Atividade principal", "SP queimados", "SP restante real"],
        [(str(i + 1), d[0], d[1], str(d[3]), str(92 - sum(x[3] for x in DAILY[: i + 1]))) for i, d in enumerate(DAILY)],
        [0.45, 0.75, 3.4, 0.9, 1.0],
        font_size=8,
    )

    doc.add_heading("05 — Daily Scrum: Reuniões Diárias da Sprint III", level=1)
    doc.add_paragraph(
        "A daily da Sprint III ocorreu majoritariamente de forma assíncrona. O registro principal foi a percepção de que a equipe estava com pouca disponibilidade por causa de outros projetos, o que tornou necessário reduzir expectativa de entrega e priorizar replanejamento."
    )
    for date, title, text, _ in DAILY:
        doc.add_heading(f"{date}/2026 — {title}", level=2)
        doc.add_paragraph(text)

    doc.add_heading("06 — Sprint Review: Revisão da Sprint III", level=1)
    doc.add_paragraph(
        "A Sprint Review registrou poucas entregas em comparação com a Sprint II. Foram validados avanços pontuais em configuração de embeddings, refatorações, separação de responsabilidades, revisão de services, transformer e backlog. As entregas maiores, especialmente endpoints REST, testes unitários e camada de embeddings completa, não foram concluídas."
    )
    add_bullets(
        doc,
        [
            "Entregas registradas no quadro: configuração de modelo LangChain para embeddings, configuração de banco para embeddings, busca híbrida em títulos, revisão de services, separação DAO/repository, transformer e documentação do backlog.",
            "Itens parcialmente avançados: popular banco com dados brutos arrumados, planejamento poker e armazenamento de embeddings no ETL.",
            "Itens não iniciados ou não fechados: endpoints por entidade, filtros de listagem, testes unitários, integração com outras bases e camada back-end completa com embeddings.",
            "Conclusão da review: a sprint não alcançou a velocidade planejada; as tarefas abertas devem compor o núcleo da próxima sprint.",
        ],
    )

    doc.add_heading("07 — Sprint Retrospective: Retrospectiva e Melhorias para Sprint IV", level=1)
    doc.add_heading("O que foi bem", level=2)
    add_bullets(
        doc,
        [
            "A equipe manteve o backlog organizado no GitHub Projects, permitindo rastrear claramente o que foi concluído, iniciado, cancelado e pendente.",
            "As tarefas concluídas ajudaram a preparar a base técnica para a próxima sprint, especialmente embeddings, refatorações e revisão de services.",
            "A equipe reconheceu cedo a baixa disponibilidade e registrou a necessidade de migração do escopo.",
        ],
    )
    doc.add_heading("O que pode melhorar", level=2)
    add_bullets(
        doc,
        [
            "O escopo planejado ficou incompatível com a disponibilidade real da equipe.",
            "As tarefas maiores ficaram abertas, principalmente endpoints, testes e camada back-end com embeddings.",
            "A comunicação assíncrona precisa ser acompanhada de decisões mais rápidas de replanejamento quando houver sobrecarga externa.",
        ],
    )
    doc.add_heading("Ações para Sprint IV", level=2)
    add_bullets(
        doc,
        [
            "Mover formalmente os 13 itens em Todo e os 3 itens em In progress para a próxima sprint.",
            "Priorizar endpoints REST por entidade e filtros de listagem antes de novas expansões de escopo.",
            "Concluir armazenamento de embeddings no ETL e validar a busca híbrida com dados reais.",
            "Criar testes unitários por módulo para reduzir risco de regressão nas refatorações.",
            "Planejar a sprint com uma capacidade menor e mais realista, considerando outros projetos acadêmicos em paralelo.",
        ],
    )

    doc.add_heading("08 — Links para os artefatos produzidos", level=1)
    add_bullets(
        doc,
        [
            f"Quadro Kanban / Backlog filtrado da Sprint III: {PROJECT_URL}",
            f"Repositório do projeto: {REPO_URL}",
            "Relatório da Sprint II usado como referência estrutural: Relatório Sprint II — Sistema de Busca de Pesquisadores.pdf",
        ],
    )

    doc.save(DOCX_PATH)
    print(DOCX_PATH)


if __name__ == "__main__":
    main()
