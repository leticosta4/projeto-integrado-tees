from dao.academic_formation_dao import AcademicFormationDao
from models.academic_formation import AcademicFormation
from psycopg_pool import ConnectionPool

class AcademicFormationService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: AcademicFormationDao = AcademicFormationDao(pool)

    def remove_all_academic_formations(self):
        return self.dao.delete_all_academic_formations()

    def add_academic_formation(
        self,
        researcher_id: int,
        level: str,
        institution: str | None = None,
        course: str | None = None,
        status: str | None = None,
        start_year: int | None = None,
        end_year: int | None = None,
        thesis_title: str | None = None,
        advisor: str | None = None,
        funding_agency: str | None = None,
        had_scholarship: bool | None = None,
    ) -> int:
        return self.dao.add_academic_formation(
            researcher_id,
            level,
            institution,
            course,
            status,
            start_year,
            end_year,
            thesis_title,
            advisor,
            funding_agency,
            had_scholarship,
        )

    def get_academic_formation_count(self) -> int:
        return self.dao.select_academic_formation_count()

    def get_academic_formations_by_researcher_id(
        self, researcher_id: int
    ) -> list[AcademicFormation]:
        return self.dao.select_academic_formations_by_researcher_id(researcher_id)
