from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.paper_dao import PaperDao
from models.paper import Paper


class PaperRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: PaperDao = PaperDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM papers
        """
        return self.dao.execute(sql)

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
        return self.dao.insert_and_return_id(
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
            ),
        )

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM papers
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

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
            last_page
        FROM papers
        WHERE title = %s
        """
        return self.dao.fetch_one(sql, (title,), row_factory=class_row(Paper))
