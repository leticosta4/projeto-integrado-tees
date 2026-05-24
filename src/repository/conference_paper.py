from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.conference_paper_dao import ConferencePaperDao
from models.conference_paper import ConferencePaper


class ConferencePaperRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ConferencePaperDao = ConferencePaperDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM conference_paper
        """
        return self.dao.execute(sql)

    def add(
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
        return self.dao.insert_and_return_id(
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

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM conference_paper
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

    def get_by_researcher_id(self, researcher_id: int) -> list[ConferencePaper]:
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
        return self.dao.fetch_all(
            sql,
            (researcher_id,),
            row_factory=class_row(ConferencePaper),
        )
