from psycopg_pool import ConnectionPool
from models.researcher import Researcher
from repository.researcher import ResearcherRepository
from etl.models import XMLData, ResearcherData

class ResearcherService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: ResearcherRepository = ResearcherRepository(pool)

    def remove_all_researchers(self):
        return self.repository.remove_all()

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
