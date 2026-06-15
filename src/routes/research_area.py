from typing import Any

from routes.crud import make_crud_blueprint


def create_research_area(service: Any, data: dict[str, Any]) -> int:
    return service.add_research_area(**data)


research_area_bp = make_crud_blueprint(
    "research_area",
    "/research-areas",
    "RESEARCH_AREA_SERVICE",
    create_research_area,
    ("researcher_id",),
)
