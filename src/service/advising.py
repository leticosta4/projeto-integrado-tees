from dao.advising_dao import AdvisingDao
from models.advising import Advising
from psycopg_pool import ConnectionPool

class AdvisingService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: AdvisingDao = AdvisingDao(pool)

    def remove_all_advisings(self):
        return self.dao.delete_all_advisings()

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
        return self.dao.add_advising(
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
        return self.dao.select_advising_count()

    def get_advisings_by_researcher_id(self, researcher_id: int) -> list[Advising]:
        return self.dao.select_advisings_by_researcher_id(researcher_id)
