from psycopg_pool import ConnectionPool
from models.researcher import Researcher
from repository.researcher import ResearcherRepository
from etl.models import XMLData, ResearcherData

class ResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: ResearcherRepository = ResearcherRepository(pool)

    def remove_all_researchers(self):
        return self.repository.remove_all()

    def insert_researcher(
        self,
        full_name: str,
        filename: str,
        filehash: str,
        lattes_id: str,
        citation_name: str | None = None,
        orcid: str | None = None,
        nationality: str | None = None,
        birth_country: str | None = None,
        birth_state: str | None = None,
        update_date: str | None = None,
    ) -> int:
        return self.repository.add(
            full_name,
            filename,
            filehash,
            lattes_id,
            citation_name,
            orcid,
            nationality,
            birth_country,
            birth_state,
            update_date,
        )

    def add_researcher(
        self,
        xml_data: XMLData
    ) -> int:
        researcher_data = xml_data.researcher_data
        return self.repository.add(
            researcher_data.full_name,
            xml_data.filename,
            xml_data.filehash,
            researcher_data.lattes_id,
            researcher_data.citation_name,
            researcher_data.orcid,
            researcher_data.nationality,
            researcher_data.birth_country,
            researcher_data.birth_state,
            researcher_data.update_date,
        )

    def get_researcher_count(self) -> int:
        return self.repository.count()

    def get_researcher_by_name(self, full_name: str) -> Researcher | None:
        return self.repository.get_by_full_name(full_name)

    def get_researcher_filehash(self, filehash: str) -> str | None:
        return self.repository.select_filehash_exists(filehash)

    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[Researcher]:
        return self.repository.list_all(filters)

    def get_by_id(self, researcher_id: int) -> Researcher | None:
        return self.repository.get_by_id(researcher_id)

    def patch(self, researcher_id: int, data: dict[str, object]) -> Researcher | None:
        return self.repository.patch(researcher_id, data)

    def remove_by_id(self, researcher_id: int) -> int:
        return self.repository.remove_by_id(researcher_id)
