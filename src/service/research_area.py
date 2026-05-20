from dao.research_area_dao import ResearchAreaDao
from models.research_area import ResearchArea
from psycopg_pool import ConnectionPool

class ResearchAreaService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ResearchAreaDao = ResearchAreaDao(pool)

    def remove_all_research_areas(self):
        return self.dao.delete_all_research_areas()

    def add_research_area(
        self,
        researcher_id: int,
        major_area: str | None = None,
        area: str | None = None,
        sub_area: str | None = None,
        specialty: str | None = None,
    ) -> int:
        return self.dao.add_research_area(
            researcher_id,
            major_area,
            area,
            sub_area,
            specialty,
        )

    def get_research_area_count(self) -> int:
        return self.dao.select_research_area_count()

    def get_research_areas_by_researcher_id(
        self, researcher_id: int
    ) -> list[ResearchArea]:
        return self.dao.select_research_areas_by_researcher_id(researcher_id)
