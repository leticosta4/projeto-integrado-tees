from flask import Blueprint, current_app, jsonify, request


search_bp = Blueprint("search", __name__, url_prefix="/search")

TYPE_ALIASES = {
    "paper": "paper",
    "papers": "paper",
    "conference paper": "conference_paper",
    "conference_paper": "conference_paper",
    "conference-paper": "conference_paper",
    "advising": "advising",
    "orientacao": "advising",
    "orientação": "advising",
}

RESULT_KIND_ALIASES = {
    "pesquisadores": "researchers",
    "researchers": "researchers",
    "researcher": "researchers",
    "publicacoes": "publications",
    "publicações": "publications",
    "publications": "publications",
    "publication": "publications",
}

DEFAULT_TYPES = {"paper", "conference_paper", "advising"}
DEFAULT_RESULT_KINDS = {"researchers", "publications"}


def _split_param(*names: str) -> list[str]:
    values: list[str] = []
    for name in names:
        for raw_value in request.args.getlist(name):
            values.extend(
                value.strip()
                for value in raw_value.split(",")
                if value.strip()
            )
    return values


def _parse_aliases(
    values: list[str],
    aliases: dict[str, str],
    default: set[str],
) -> set[str]:
    if not values:
        return default

    parsed = {
        aliases[value.lower()]
        for value in values
        if value.lower() in aliases
    }
    return parsed


def _optional_int(name: str) -> tuple[int | None, tuple[object, int] | None]:
    value = request.args.get(name)

    if value is None or value == "":
        return None, None

    try:
        return int(value), None
    except ValueError:
        return None, (jsonify({"error": f"Query parameter '{name}' must be an integer"}), 400)


@search_bp.get("")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({"error": "Query parameter 'limit' must be an integer"}), 400

    year_from, error = _optional_int("year_from")
    if error:
        return error

    year_to, error = _optional_int("year_to")
    if error:
        return error

    researcher_id, error = _optional_int("researcher_id")
    if error:
        return error

    types = _parse_aliases(
        _split_param("type", "types"),
        TYPE_ALIASES,
        DEFAULT_TYPES,
    )
    result_kinds = _parse_aliases(
        _split_param("result_kind", "result_kinds"),
        RESULT_KIND_ALIASES,
        DEFAULT_RESULT_KINDS,
    )
    area = request.args.get("area", "").strip() or None

    service = current_app.config["SEARCH_SERVICE"]
    return jsonify(
        service.search(
            query=query,
            types=types,
            result_kinds=result_kinds,
            limit=limit,
            year_from=year_from,
            year_to=year_to,
            area=area,
            researcher_id=researcher_id,
        )
    )
