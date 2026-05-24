from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.advising_dao import AdvisingDao
from models.advising import Advising


class AdvisingRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: AdvisingDao = AdvisingDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM advising
        """
        return self.dao.execute(sql)

    def add(
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
        return self.dao.insert_and_return_id(
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

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM advising
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

    def get_by_researcher_id(self, researcher_id: int) -> list[Advising]:
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
        return self.dao.fetch_all(
            sql,
            (researcher_id,),
            row_factory=class_row(Advising),
        )
