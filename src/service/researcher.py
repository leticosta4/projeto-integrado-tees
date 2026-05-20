from psycopg_pool import ConnectionPool
from dao.researcher_dao import ResearcherDao
from models.researcher import Researcher

class ResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ResearcherDao = ResearcherDao(pool)

    def remove_all_researchers(self):
        return self.dao.delete_all_researchers()

    def add_researcher(
        self,
        full_name: str,
        lattes_id: str,
        citation_name: str | None = None,
        orcid: str | None = None,
        nationality: str | None = None,
        birth_country: str | None = None,
        birth_state: str | None = None,
        update_date: str | None = None,
    ) -> int:
        return self.dao.add_researcher(
            full_name,
            lattes_id,
            citation_name,
            orcid,
            nationality,
            birth_country,
            birth_state,
            update_date,
        )

    def get_researcher_count(self) -> int:
        return self.dao.select_researcher_count()

    def get_researcher_by_name(self, full_name: str) -> Researcher | None:
        return self.dao.select_researcher_by_full_name(full_name)
