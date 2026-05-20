from models.paper import Paper
from dao.paper_dao import PaperDao
from psycopg_pool import ConnectionPool

class PaperService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: PaperDao = PaperDao(pool)

    def remove_all_papers(self):
        return self.dao.delete_all_papers()

    def add_paper(
        self,
        title: str,
        researcher_id: int,
        year: int | None = None,
        doi: str | None = None,
        language: str | None = None,
        nature: str | None = None,
        country: str | None = None,
        journal: str | None = None,
        issn: str | None = None,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> int:
        return self.dao.add_paper(
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page,
        )

    def insert_paper(
        self,
        title: str,
        researcher_id: int,
        year: int | None = None,
        doi: str | None = None,
        language: str | None = None,
        nature: str | None = None,
        country: str | None = None,
        journal: str | None = None,
        issn: str | None = None,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> int:
        return self.add_paper(
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page,
        )

    def get_paper_count(self) -> int:
        return self.dao.select_paper_count()

    def get_paper_by_title(self, title: str) -> Paper | None:
        return self.dao.select_paper_by_title(title)
