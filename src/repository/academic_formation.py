from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.academic_formation import AcademicFormation


class AcademicFormationRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def remove_all(self) -> int:
        sql = """
        DELETE FROM academic_formation
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount

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
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
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
                row = cur.fetchone()
                return row[0] if row else 0

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM academic_formation
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

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
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(AcademicFormation)) as cur:
                _ = cur.execute(sql, (researcher_id,))
                return cur.fetchall()
