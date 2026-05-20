from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models.paper import Paper

class PaperDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def delete_all_papers(self) -> int:
        sql = """
        DELETE FROM papers
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)

                return cur.rowcount

    def add_paper(
        self,
        title: str,
        researcher_id: int,
        year: int | None = None,
        doi: str | None = None,
        language: str | None = None,
        nature: str | None = None,
        country: str | None = None,
        journal: str | None = None,
        issn: str | None = None,
        volume: str | None = None,
        issue: str | None = None,
        first_page: str | None = None,
        last_page: str | None = None,
    ) -> int:
        sql = """
        INSERT INTO papers
        (
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (
                        title,
                        researcher_id,
                        year,
                        doi,
                        language,
                        nature,
                        country,
                        journal,
                        issn,
                        volume,
                        issue,
                        first_page,
                        last_page,
                    )
                )

                row = cur.fetchone()
                return row[0] if row else 0

    def select_paper_count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM papers
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def select_paper_by_title(self, title: str) -> Paper | None:
        sql = """
        SELECT
            id,
            title,
            researcher_id,
            year,
            doi,
            language,
            nature,
            country,
            journal,
            issn,
            volume,
            issue,
            first_page,
            last_page
        FROM papers
        WHERE title = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(sql, (title,))
                return cur.fetchone()
