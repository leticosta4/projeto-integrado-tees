from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.research_area_dao import ResearchAreaDao
from models.research_area import ResearchArea


class ResearchAreaRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ResearchAreaDao = ResearchAreaDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM research_area
        """
        return self.dao.execute(sql)

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
        return self.dao.insert_and_return_id(
            sql,
            (
                researcher_id,
                major_area,
                area,
                sub_area,
                specialty,
            ),
        )

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM research_area
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

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
        return self.dao.fetch_all(
            sql,
            (researcher_id,),
            row_factory=class_row(ResearchArea),
        )
