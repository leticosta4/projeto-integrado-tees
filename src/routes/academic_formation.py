from typing import Any

from routes.crud import make_crud_blueprint


def create_academic_formation(service: Any, data: dict[str, Any]) -> int:
    return service.add_academic_formation(**data)


academic_formation_bp = make_crud_blueprint(
    "academic_formation",
    "/academic-formations",
    "ACADEMIC_FORMATION_SERVICE",
    create_academic_formation,
    ("researcher_id", "level"),
)
