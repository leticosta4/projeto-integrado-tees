from psycopg_pool import ConnectionPool

from models.conference_paper import ConferencePaper
from repository.conference_paper import ConferencePaperRepository

class ConferencePaperService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: ConferencePaperRepository = ConferencePaperRepository(pool)


    def remove_all_conference_papers(self):
        return self.repository.remove_all()


    def add_conference_paper(
        self,
        researcher_id: int,
        title: str,
        year: int | None = None,
        nature: str | None = None,
        country: str | None = None,
        language: str | None = None,
        doi: str | None = None,
        event_name: str | None = None,
        event_city: str | None = None,
        event_year: int | None = None,
        event_classification: str | None = None,
        proceedings_title: str | None = None,
        isbn: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> int:
        return self.repository.add(
            researcher_id,
            title,
            year,
            nature,
            country,
            language,
            doi,
            event_name,
            event_city,
            event_year,
            event_classification,
            proceedings_title,
            isbn,
            first_page,
            last_page,
        )


    def get_conference_paper_count(self) -> int:
        return self.repository.count()


    def get_conference_papers_by_researcher_id(
        self, researcher_id: int
    ) -> list[ConferencePaper]:
        return self.repository.get_by_researcher_id(researcher_id)


    def list_all(self, filters: dict[str, object] | None = None) -> list[ConferencePaper]:
        return self.repository.list_all(filters)
    