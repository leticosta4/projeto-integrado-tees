from typing import Any

from routes.crud import make_crud_blueprint


def create_researcher(service: Any, data: dict[str, Any]) -> int:
    return service.create_researcher(**data)


researcher_bp = make_crud_blueprint(
    "researcher",
    "/researchers",
    "RESEARCHER_SERVICE",
    create_researcher,
    ("full_name", "filename", "filehash", "lattes_id"),
)
