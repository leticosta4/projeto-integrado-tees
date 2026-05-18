from psycopg_pool import ConnectionPool
from researcher_dao import ResearcherDao
from models import Researcher

class ResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ResearcherDao = ResearcherDao(pool)

    def remove_all_researchers(self):
        return self.dao.delete_all_researchers()

    def insert_researcher(self, full_name: str) -> int:
        return self.dao.insert_researcher(full_name)

    def get_researcher_count(self) -> int:
        return self.dao.select_researcher_count()

    def get_researcher_by_name(self, full_name: str) -> Researcher | None:
        return self.dao.select_researcher_by_full_name(full_name)
