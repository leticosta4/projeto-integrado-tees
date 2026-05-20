from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models.conference_paper import ConferencePaper

class ConferencePaperDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def delete_all_conference_papers(self) -> int:
        sql = """
        DELETE FROM conference_paper
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount

    def add_conference_paper(
        self,
        researcher_id: int,
        title: str,
        year: int | None = None,
        nature: str | None = None,
        country: str | None = None,
        language: str | None = None,
        doi: str | None = None,
        event_name: str | None = None,
        event_city: str | None = None,
        event_year: int | None = None,
        event_classification: str | None = None,
        proceedings_title: str | None = None,
        isbn: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> int:
        sql = """
        INSERT INTO conference_paper
        (
            researcher_id,
            title,
            year,
            nature,
            country,
            language,
            doi,
            event_name,
            event_city,
            event_year,
            event_classification,
            proceedings_title,
            isbn,
            first_page,
            last_page
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (
                        researcher_id,
                        title,
                        year,
                        nature,
                        country,
                        language,
                        doi,
                        event_name,
                        event_city,
                        event_year,
                        event_classification,
                        proceedings_title,
                        isbn,
                        first_page,
                        last_page,
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0

    def select_conference_paper_count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM conference_paper
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def select_conference_papers_by_researcher_id(
        self, researcher_id: int
    ) -> list[ConferencePaper]:
        sql = """
        SELECT
            id,
            researcher_id,
            title,
            year,
            nature,
            country,
            language,
            doi,
            event_name,
            event_city,
            event_year,
            event_classification,
            proceedings_title,
            isbn,
            first_page,
            last_page
        FROM conference_paper
        WHERE researcher_id = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ConferencePaper)) as cur:
                _ = cur.execute(sql, (researcher_id,))
                return cur.fetchall()
