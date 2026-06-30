from psycopg_pool import ConnectionPool

from models.paper_researcher import PaperResearcher
from repository.paper_researcher import PaperResearcherRepository


class PaperResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: PaperResearcherRepository = PaperResearcherRepository(pool)


    def add_paper_researcher(
        self,
        paper_id: int,
        researcher_id: int,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> PaperResearcher | None:
        return self.repository.add(
            paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by,
        )


    def get_paper_researcher_count(self) -> int:
        return self.repository.count()


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[PaperResearcher]:
        return self.repository.list_all(filters)


    def get_by_paper_id(self, paper_id: int) -> list[PaperResearcher]:
        return self.repository.get_by_paper_id(paper_id)


    def get_by_researcher_id(self, researcher_id: int) -> list[PaperResearcher]:
        return self.repository.get_by_researcher_id(researcher_id)


    def get(
        self,
        paper_id: int,
        researcher_id: int,
    ) -> PaperResearcher | None:
        return self.repository.get(paper_id, researcher_id)


    def remove(
        self,
        paper_id: int,
        researcher_id: int,
    ) -> int:
        return self.repository.remove(paper_id, researcher_id)
