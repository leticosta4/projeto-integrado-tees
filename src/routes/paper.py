from typing import Any

from flask import current_app, jsonify, request

from routes.crud import make_crud_blueprint, model_to_dict


def create_paper(service: Any, data: dict[str, Any]) -> int:
    return service.add_paper(**data)


paper_bp = make_crud_blueprint(
    "paper",
    "/papers",
    "PAPER_SERVICE",
    create_paper,
    ("title", "researcher_id"),
)


@paper_bp.get("/search")
def search_papers():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "Query parameter 'limit' must be an integer"}), 400

    service = current_app.config["PAPER_SERVICE"]
    results = [
        {"paper": model_to_dict(paper), "score": score}
        for paper, score in service.hybrid_search(query, limit)
    ]
    return jsonify(results)
