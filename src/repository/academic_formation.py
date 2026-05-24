from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.academic_formation_dao import AcademicFormationDao
from models.academic_formation import AcademicFormation


class AcademicFormationRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: AcademicFormationDao = AcademicFormationDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM academic_formation
        """
        return self.dao.execute(sql)

    def add(
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
        sql = """
        INSERT INTO academic_formation
        (
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
            had_scholarship
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.dao.insert_and_return_id(
            sql,
            (
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
            ),
        )

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM academic_formation
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

    def get_by_researcher_id(self, researcher_id: int) -> list[AcademicFormation]:
        sql = """
        SELECT
            id,
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
            had_scholarship
        FROM academic_formation
        WHERE researcher_id = %s
        """
        return self.dao.fetch_all(
            sql,
            (researcher_id,),
            row_factory=class_row(AcademicFormation),
        )
