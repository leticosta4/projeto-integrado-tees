from domain.paper.models import Paper
from domain.paper.paper_dao import PaperDao
from psycopg_pool import ConnectionPool

class PaperService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: PaperDao = PaperDao(pool)

    def remove_all_papers(self):
        return self.dao.delete_all_papers()

    def insert_paper(self, title: str, researcher_id: int) -> int:
        return self.dao.insert_paper(title, researcher_id)

    def get_paper_count(self) -> int:
        return self.dao.select_paper_count()

    def get_paper_by_title(self, title: str) -> Paper | None:
        return self.dao.select_paper_by_title(title)
