from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models import Paper

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

    def insert_paper(self, title: str, researcher_id: int) -> int:
        sql = """
        INSERT INTO papers
        (title, researcher)
        VALUES
        (%s, %s)
        RETURNING id
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (title, researcher_id)
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
        SELECT id, title, researcher_id
        FROM researcher
        WHERE title = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(sql, (title,))
                return cur.fetchone()
