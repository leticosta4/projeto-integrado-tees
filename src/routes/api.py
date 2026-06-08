from collections.abc import Callable
from typing import Any

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel

api = Blueprint("api", __name__, url_prefix="/api")


def serialize(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")


def payload() -> dict[str, Any]:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def filters() -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for key, value in request.args.items():
        if value == "":
            continue
        parsed[key] = parse_query_value(value)
    return parsed


def parse_query_value(value: str) -> str | int | bool:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"

    try:
        return int(value)
    except ValueError:
        return value


def not_found(entity: str):
    return jsonify({"error": f"{entity} not found"}), 404


def created(item_id: int):
    return jsonify({"id": item_id}), 201


def register_crud_routes(
    entity: str,
    service_key: str,
    create: Callable[[Any, dict[str, Any]], int],
) -> None:
    collection_path = f"/{entity}"
    item_path = f"/{entity}/<int:item_id>"

    @api.get(collection_path, endpoint=f"{entity}_list")
    def list_items(service_key=service_key):
        service = current_app.config[service_key]
        items = service.list_all(filters())
        return jsonify([serialize(item) for item in items])

    @api.get(item_path, endpoint=f"{entity}_get")
    def get_item(item_id: int, service_key=service_key, entity=entity):
        service = current_app.config[service_key]
        item = service.get_by_id(item_id)
        if item is None:
            return not_found(entity)

        return jsonify(serialize(item))

    @api.post(collection_path, endpoint=f"{entity}_create")
    def create_item(service_key=service_key, create=create):
        service = current_app.config[service_key]
        try:
            item_id = create(service, payload())
        except KeyError as error:
            return jsonify({"error": f"missing required field {error.args[0]}"}), 400

        return created(item_id)

    @api.patch(item_path, endpoint=f"{entity}_patch")
    def patch_item(item_id: int, service_key=service_key, entity=entity):
        service = current_app.config[service_key]
        item = service.patch(item_id, payload())
        if item is None:
            return not_found(entity)

        return jsonify(serialize(item))

    @api.delete(item_path, endpoint=f"{entity}_delete")
    def delete_item(item_id: int, service_key=service_key):
        service = current_app.config[service_key]
        deleted = service.remove_by_id(item_id)
        return jsonify({"deleted": deleted})


def create_researcher(service, data: dict[str, Any]) -> int:
    return service.insert_researcher(
        data["full_name"],
        data.get("filename", ""),
        data.get("filehash", ""),
        data["lattes_id"],
        data.get("citation_name"),
        data.get("orcid"),
        data.get("nationality"),
        data.get("birth_country"),
        data.get("birth_state"),
        data.get("update_date"),
    )


def create_paper(service, data: dict[str, Any]) -> int:
    return service.add_paper(
        data["title"],
        data["researcher_id"],
        data.get("year"),
        data.get("doi"),
        data.get("language"),
        data.get("nature"),
        data.get("country"),
        data.get("journal"),
        data.get("issn"),
        data.get("volume"),
        data.get("issue"),
        data.get("first_page"),
        data.get("last_page"),
        data.get("title_embeddings"),
    )


def create_academic_formation(service, data: dict[str, Any]) -> int:
    return service.add_academic_formation(
        data["researcher_id"],
        data["level"],
        data.get("institution"),
        data.get("course"),
        data.get("status"),
        data.get("start_year"),
        data.get("end_year"),
        data.get("thesis_title"),
        data.get("advisor"),
        data.get("funding_agency"),
        data.get("had_scholarship"),
    )


def create_research_area(service, data: dict[str, Any]) -> int:
    return service.add_research_area(
        data["researcher_id"],
        data.get("major_area"),
        data.get("area"),
        data.get("sub_area"),
        data.get("specialty"),
    )


def create_conference_paper(service, data: dict[str, Any]) -> int:
    return service.add_conference_paper(
        data["researcher_id"],
        data["title"],
        data.get("year"),
        data.get("nature"),
        data.get("country"),
        data.get("language"),
        data.get("doi"),
        data.get("event_name"),
        data.get("event_city"),
        data.get("event_year"),
        data.get("event_classification"),
        data.get("proceedings_title"),
        data.get("isbn"),
        data.get("first_page"),
        data.get("last_page"),
    )


def create_advising(service, data: dict[str, Any]) -> int:
    return service.add_advising(
        data["researcher_id"],
        data["level"],
        data["title"],
        data.get("year"),
        data.get("advisee_name"),
        data.get("advising_type"),
        data.get("institution"),
        data.get("course"),
        data.get("country"),
        data.get("had_scholarship"),
        data.get("funding_agency"),
    )


register_crud_routes("researchers", "RESEARCHER_SERVICE", create_researcher)
register_crud_routes("papers", "PAPER_SERVICE", create_paper)
register_crud_routes(
    "academic-formations",
    "ACADEMIC_FORMATION_SERVICE",
    create_academic_formation,
)
register_crud_routes("research-areas", "RESEARCH_AREA_SERVICE", create_research_area)
register_crud_routes(
    "conference-papers",
    "CONFERENCE_PAPER_SERVICE",
    create_conference_paper,
)
register_crud_routes("advisings", "ADVISING_SERVICE", create_advising)


@api.get("/papers/search")
def search_papers():
    query = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", "10"))
    if not query:
        return jsonify({"error": "query parameter q is required"}), 400

    paper_service = current_app.config["PAPER_SERVICE"]
    try:
        results = paper_service.hybrid_search(query, limit)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(
        [
            {
                "paper": serialize(paper),
                "score": score,
            }
            for paper, score in results
        ]
    )
