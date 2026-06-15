from typing import Any

from routes.crud import make_crud_blueprint


def create_advising(service: Any, data: dict[str, Any]) -> int:
    return service.add_advising(**data)


advising_bp = make_crud_blueprint(
    "advising",
    "/advisings",
    "ADVISING_SERVICE",
    create_advising,
    ("researcher_id", "level", "title"),
)
