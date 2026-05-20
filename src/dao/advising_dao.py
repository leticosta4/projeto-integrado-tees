from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models.advising import Advising

class AdvisingDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def delete_all_advisings(self) -> int:
        sql = """
        DELETE FROM advising
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount

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
        sql = """
        INSERT INTO advising
        (
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
            funding_agency
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
                        title,
                        year,
                        advisee_name,
                        advising_type,
                        institution,
                        course,
                        country,
                        had_scholarship,
                        funding_agency,
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0

    def select_advising_count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM advising
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def select_advisings_by_researcher_id(self, researcher_id: int) -> list[Advising]:
        sql = """
        SELECT
            id,
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
            funding_agency
        FROM advising
        WHERE researcher_id = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Advising)) as cur:
                _ = cur.execute(sql, (researcher_id,))
                return cur.fetchall()
