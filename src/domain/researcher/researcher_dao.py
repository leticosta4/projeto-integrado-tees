from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models import Researcher

class ResearcherDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def delete_all_researchers(self) -> int:
        sql = """
        DELETE FROM researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)

                return cur.rowcount

    def insert_researcher(self, full_name: str) -> int:
        sql = """
        INSERT INTO researcher
        (full_name)
        VALUES
        (%s)
        RETURNING id
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (full_name,)
                )

                row = cur.fetchone()
                return row[0] if row else 0

    def select_researcher_count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM researcher
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def select_researcher_by_full_name(self, full_name: str) -> Researcher | None:
        sql = """
        SELECT id, full_name
        FROM researcher
        WHERE full_name = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Researcher)) as cur:
                _ = cur.execute(sql, (full_name,))
                return cur.fetchone()
