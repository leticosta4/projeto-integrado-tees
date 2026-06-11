from psycopg_pool import ConnectionPool

from models.research_area import ResearchArea
from repository.research_area import ResearchAreaRepository

class ResearchAreaService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: ResearchAreaRepository = ResearchAreaRepository(pool)


    def remove_all_research_areas(self):
        return self.repository.remove_all()


    def add_research_area(
        self,
        researcher_id: int,
        major_area: str | None = None,
        area: str | None = None,
        sub_area: str | None = None,
        specialty: str | None = None,
    ) -> int:
        return self.repository.add(
            researcher_id,
            major_area,
            area,
            sub_area,
            specialty,
        )


    def get_research_area_count(self) -> int:
        return self.repository.count()


    def get_research_areas_by_researcher_id(
        self, researcher_id: int
    ) -> list[ResearchArea]:
        return self.repository.get_by_researcher_id(researcher_id)


    def list_all(self, filters: dict[str, object] | None = None) -> list[ResearchArea]:
        return self.repository.list_all(filters)
    