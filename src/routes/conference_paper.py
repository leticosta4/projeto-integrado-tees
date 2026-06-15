from typing import Any

from routes.crud import make_crud_blueprint


def create_conference_paper(service: Any, data: dict[str, Any]) -> int:
    return service.add_conference_paper(**data)


conference_paper_bp = make_crud_blueprint(
    "conference_paper",
    "/conference-papers",
    "CONFERENCE_PAPER_SERVICE",
    create_conference_paper,
    ("researcher_id", "title"),
)
