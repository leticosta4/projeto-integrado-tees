from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.research_area import ResearchArea
from repository.crud import get_by_id, list_all, patch_by_id, remove_by_id


RESEARCH_AREA_COLUMNS = [
    "id",
    "researcher_id",
    "major_area",
    "area",
    "sub_area",
    "specialty",
]


class ResearchAreaRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def remove_all(self) -> int:
        sql = """
        DELETE FROM research_area
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount


    def add(
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


    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM research_area
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0


    def get_by_researcher_id(self, researcher_id: int) -> list[ResearchArea]:
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


    def list_all(self, filters: dict[str, object] | None = None) -> list[ResearchArea]:
        return list_all(
            self.pool,
            "research_area",
            RESEARCH_AREA_COLUMNS,
            ResearchArea,
            filters,
        )
    

    def get_by_id(self, area_id: int) -> ResearchArea | None:
        return get_by_id(
            self.pool,
            "research_area",
            RESEARCH_AREA_COLUMNS,
            ResearchArea,
            area_id,
        )


    def patch(self, area_id: int, data: dict[str, object]) -> ResearchArea | None:
        return patch_by_id(
            self.pool,
            "research_area",
            RESEARCH_AREA_COLUMNS,
            ResearchArea,
            area_id,
            data,
        )


    def remove_by_id(self, area_id: int) -> int:
        return remove_by_id(self.pool, "research_area", area_id)


    def get_by_researcher_id(self, researcher_id: int) -> list[ResearchArea]:
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