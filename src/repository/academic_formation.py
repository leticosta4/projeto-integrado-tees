from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.academic_formation import AcademicFormation
from repository.crud import get_by_id, list_all, patch_by_id, remove_by_id


ACADEMIC_FORMATION_COLUMNS = [
    "id",
    "researcher_id",
    "level",
    "institution",
    "course",
    "status",
    "start_year",
    "end_year",
    "thesis_title",
    "advisor",
    "funding_agency",
    "had_scholarship",
]


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
            
    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[AcademicFormation]:
        return list_all(
            self.pool,
            "academic_formation",
            ACADEMIC_FORMATION_COLUMNS,
            AcademicFormation,
            filters,
        )
    

    def get_by_id(self, formation_id: int) -> AcademicFormation | None:
        return get_by_id(
            self.pool,
            "academic_formation",
            ACADEMIC_FORMATION_COLUMNS,
            AcademicFormation,
            formation_id,
        )


    def patch(
        self,
        formation_id: int,
        data: dict[str, object],
    ) -> AcademicFormation | None:
        return patch_by_id(
            self.pool,
            "academic_formation",
            ACADEMIC_FORMATION_COLUMNS,
            AcademicFormation,
            formation_id,
            data,
        )


    def remove_by_id(self, formation_id: int) -> int:
        return remove_by_id(self.pool, "academic_formation", formation_id)


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
