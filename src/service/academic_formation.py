from psycopg_pool import ConnectionPool

from models.academic_formation import AcademicFormation
from repository.academic_formation import AcademicFormationRepository

class AcademicFormationService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: AcademicFormationRepository = AcademicFormationRepository(pool)

    def remove_all_academic_formations(self):
        return self.repository.remove_all()

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
        return self.repository.add(
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
        return self.repository.count()

    def get_academic_formations_by_researcher_id(
        self, researcher_id: int
    ) -> list[AcademicFormation]:
        return self.repository.get_by_researcher_id(researcher_id)
