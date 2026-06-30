from flask import Blueprint, Response, current_app, jsonify, request

from routes.crud import get_json_payload, model_to_dict, validate_required


conference_paper_researcher_bp = Blueprint(
    "conference_paper_researcher",
    __name__,
    url_prefix="/conference-paper-researchers",
)


def _int_arg(name: str) -> tuple[int | None, tuple[Response, int] | None]:
    value = request.args.get(name)

    if value is None or value == "":
        return None, (jsonify({"error": f"Query parameter '{name}' is required"}), 400)

    try:
        return int(value), None
    except ValueError:
        return None, (jsonify({"error": f"Query parameter '{name}' must be an integer"}), 400)


@conference_paper_researcher_bp.get("")
def list_conference_paper_researchers():
    service = current_app.config["CONFERENCE_PAPER_RESEARCHER_SERVICE"]
    links = service.list_all(request.args.to_dict())
    return jsonify(model_to_dict(links))


@conference_paper_researcher_bp.post("")
def create_conference_paper_researcher():
    service = current_app.config["CONFERENCE_PAPER_RESEARCHER_SERVICE"]
    payload, error = get_json_payload()

    if error:
        return error

    assert payload is not None
    missing_error = validate_required(
        payload,
        ("conference_paper_id", "researcher_id"),
    )

    if missing_error:
        return missing_error

    link = service.add_conference_paper_researcher(**payload)
    response = jsonify(model_to_dict(link))
    response.status_code = 201
    return response


@conference_paper_researcher_bp.get("/link")
def get_conference_paper_researcher():
    service = current_app.config["CONFERENCE_PAPER_RESEARCHER_SERVICE"]
    conference_paper_id, error = _int_arg("conference_paper_id")

    if error:
        return error

    researcher_id, error = _int_arg("researcher_id")

    if error:
        return error

    assert conference_paper_id is not None
    assert researcher_id is not None
    link = service.get(conference_paper_id, researcher_id)

    if link is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify(model_to_dict(link))


@conference_paper_researcher_bp.delete("/link")
def delete_conference_paper_researcher():
    service = current_app.config["CONFERENCE_PAPER_RESEARCHER_SERVICE"]
    conference_paper_id, error = _int_arg("conference_paper_id")

    if error:
        return error

    researcher_id, error = _int_arg("researcher_id")

    if error:
        return error

    assert conference_paper_id is not None
    assert researcher_id is not None
    removed_count = service.remove(conference_paper_id, researcher_id)

    if removed_count == 0:
        return jsonify({"error": "Not found"}), 404

    return "", 204
