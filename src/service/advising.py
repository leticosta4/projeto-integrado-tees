from psycopg_pool import ConnectionPool

from models.advising import Advising
from repository.advising import AdvisingRepository

class AdvisingService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: AdvisingRepository = AdvisingRepository(pool)


    def remove_all_advisings(self):
        return self.repository.remove_all()


    def add_advising(
        self,
        researcher_id: int,
        level: str,
        title: str,
        year: int | None = None,
        advisee_name: str | None = None,
        advising_type: str | None = None,
        institution: str | None = None,
        course: str | None = None,
        country: str | None = None,
        had_scholarship: bool | None = None,
        funding_agency: str | None = None,
    ) -> int:
        return self.repository.add(
            researcher_id,
            level,
            title,
            year,
            advisee_name,
            advising_type,
            institution,
            course,
            country,
            had_scholarship,
            funding_agency,
        )


    def get_advising_count(self) -> int:
        return self.repository.count()


    def get_advisings_by_researcher_id(self, researcher_id: int) -> list[Advising]:
        return self.repository.get_by_researcher_id(researcher_id)

    def list_all(self, filters: dict[str, object] | None = None) -> list[Advising]:
        return self.repository.list_all(filters)
    