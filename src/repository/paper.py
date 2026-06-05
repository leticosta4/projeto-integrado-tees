from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.paper import Paper


class PaperRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def remove_all(self) -> int:
        sql = """
        DELETE FROM papers
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount

    def add(
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
        title_embeddings: list[float] | None = None,
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
            last_page,
            title_embeddings
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        title_embeddings,
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM papers
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def get_by_title(self, title: str) -> Paper | None:
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
            last_page,
            title_embeddings
        FROM papers
        WHERE title = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(sql, (title,))
                return cur.fetchone()
