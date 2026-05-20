from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from models.research_area import ResearchArea

class ResearchAreaDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def delete_all_research_areas(self) -> int:
        sql = """
        DELETE FROM research_area
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount

    def add_research_area(
        self,
        researcher_id: int,
        major_area: str | None = None,
        area: str | None = None,
        sub_area: str | None = None,
        specialty: str | None = None,
    ) -> int:
        sql = """
        INSERT INTO research_area
        (
            researcher_id,
            major_area,
            area,
            sub_area,
            specialty
        )
        VALUES
        (%s, %s, %s, %s, %s)
        RETURNING id
        """

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (
                        researcher_id,
                        major_area,
                        area,
                        sub_area,
                        specialty,
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0

    def select_research_area_count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM research_area
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

    def select_research_areas_by_researcher_id(
        self, researcher_id: int
    ) -> list[ResearchArea]:
        sql = """
        SELECT
            id,
            researcher_id,
            major_area,
            area,
            sub_area,
            specialty
        FROM research_area
        WHERE researcher_id = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ResearchArea)) as cur:
                _ = cur.execute(sql, (researcher_id,))
                return cur.fetchall()
