from psycopg_pool import ConnectionPool

from models.conference_paper_researcher import ConferencePaperResearcher
from repository.conference_paper_researcher import ConferencePaperResearcherRepository


class ConferencePaperResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: ConferencePaperResearcherRepository = (
            ConferencePaperResearcherRepository(pool)
        )


    def add_conference_paper_researcher(
        self,
        conference_paper_id: int,
        researcher_id: int,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> ConferencePaperResearcher | None:
        return self.repository.add(
            conference_paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by,
        )


    def get_conference_paper_researcher_count(self) -> int:
        return self.repository.count()


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[ConferencePaperResearcher]:
        return self.repository.list_all(filters)


    def get_by_conference_paper_id(
        self,
        conference_paper_id: int,
    ) -> list[ConferencePaperResearcher]:
        return self.repository.get_by_conference_paper_id(conference_paper_id)


    def get_by_researcher_id(
        self,
        researcher_id: int,
    ) -> list[ConferencePaperResearcher]:
        return self.repository.get_by_researcher_id(researcher_id)


    def get(
        self,
        conference_paper_id: int,
        researcher_id: int,
    ) -> ConferencePaperResearcher | None:
        return self.repository.get(conference_paper_id, researcher_id)


    def remove(
        self,
        conference_paper_id: int,
        researcher_id: int,
    ) -> int:
        return self.repository.remove(conference_paper_id, researcher_id)
