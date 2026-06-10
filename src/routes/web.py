from typing import Any

from flask import Blueprint, current_app, render_template, request

web = Blueprint("web", __name__)


@web.get("/")
def landing_page():
    return render_template("pages/landing.html")


@web.get("/inicio")
def prototype_home_page():
    query = request.args.get("q", "").strip()
    results: list[dict[str, Any]] = []
    search_error = None
    search_mode = None

    if query:
        paper_service = current_app.config["PAPER_SERVICE"]
        researcher_service = current_app.config["RESEARCHER_SERVICE"]

        try:
            matches = paper_service.hybrid_search(query, limit=10)
            search_mode = "Busca hibrida"
        except ValueError:
            matches = [(paper, None) for paper in paper_service.list_all({"title": query})[:10]]
            search_mode = "Busca textual"
        except Exception as error:
            matches = []
            search_error = str(error)

        for paper, score in matches:
            researcher = researcher_service.get_by_id(paper.researcher_id)
            results.append(
                {
                    "paper": paper,
                    "score": score,
                    "researcher_name": (
                        researcher.full_name if researcher else "Pesquisador nao encontrado"
                    ),
                    "summary": build_paper_summary(paper),
                }
            )

    return render_template(
        "pages/prototype_home.html",
        query=query,
        results=results,
        search_error=search_error,
        search_mode=search_mode,
    )


def build_paper_summary(paper) -> str:
    details = [
        paper.journal,
        paper.nature,
        paper.country,
        paper.language,
        f"DOI: {paper.doi}" if paper.doi else None,
    ]
    summary = ", ".join(detail for detail in details if detail)
    return summary or "Resumo curto do artigo, livro ou tese sendo exibido."
