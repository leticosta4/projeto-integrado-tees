from typing import Any

from flask import Blueprint, current_app, jsonify, request


analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

TYPE_ALIASES = {
    "paper": "paper",
    "papers": "paper",
    "artigo": "paper",
    "artigo de periodico": "paper",
    "conference paper": "conference_paper",
    "conference_paper": "conference_paper",
    "conference-paper": "conference_paper",
    "trabalho em evento": "conference_paper",
    "advising": "advising",
    "orientacao": "advising",
}

DEFAULT_TYPES = {"paper", "conference_paper", "advising"}


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


def _parse_types() -> set[str]:
    values = _split_param("type", "types")
    if not values:
        return DEFAULT_TYPES

    return {
        TYPE_ALIASES[value.lower()]
        for value in values
        if value.lower() in TYPE_ALIASES
    }


def _optional_int(name: str) -> tuple[int | None, tuple[Any, int] | None]:
    value = request.args.get(name)

    if value is None or value == "":
        return None, None

    try:
        return int(value), None
    except ValueError:
        return None, (jsonify({"error": f"Query parameter '{name}' must be an integer"}), 400)


def _filters() -> tuple[dict[str, object], tuple[Any, int] | None]:
    year_from, error = _optional_int("year_from")
    if error:
        return {}, error

    year_to, error = _optional_int("year_to")
    if error:
        return {}, error

    limit, error = _optional_int("limit")
    if error:
        return {}, error

    return {
        "types": _parse_types(),
        "year_from": year_from,
        "year_to": year_to,
        "area": request.args.get("area", "").strip() or None,
        "limit": limit,
    }, None


@analytics_bp.get("/summary")
def summary():
    filters, error = _filters()
    if error:
        return error

    service = current_app.config["ANALYTICS_SERVICE"]
    return jsonify(
        service.summary(
            types=filters["types"],
            year_from=filters["year_from"],
            year_to=filters["year_to"],
            area=filters["area"],
        )
    )


@analytics_bp.get("/publications-by-year")
def publications_by_year():
    filters, error = _filters()
    if error:
        return error

    service = current_app.config["ANALYTICS_SERVICE"]
    return jsonify(service.publications_by_year(**_analytics_kwargs(filters)))


@analytics_bp.get("/publications-by-area")
def publications_by_area():
    filters, error = _filters()
    if error:
        return error

    service = current_app.config["ANALYTICS_SERVICE"]
    return jsonify(
        service.publications_by_area(
            **_analytics_kwargs(filters),
            limit=filters["limit"] or 10,
        )
    )


@analytics_bp.get("/top-researchers")
def top_researchers():
    filters, error = _filters()
    if error:
        return error

    service = current_app.config["ANALYTICS_SERVICE"]
    return jsonify(
        service.top_researchers(
            **_analytics_kwargs(filters),
            limit=filters["limit"] or 8,
        )
    )


@analytics_bp.get("/coauthor-network")
def coauthor_network():
    filters, error = _filters()
    if error:
        return error

    service = current_app.config["ANALYTICS_SERVICE"]
    return jsonify(
        service.coauthor_network(
            **_analytics_kwargs(filters),
            limit=filters["limit"] or 50,
        )
    )


def _analytics_kwargs(filters: dict[str, object]) -> dict[str, object]:
    return {
        "types": filters["types"],
        "year_from": filters["year_from"],
        "year_to": filters["year_to"],
        "area": filters["area"],
    }
