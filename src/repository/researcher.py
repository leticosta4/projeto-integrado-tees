from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from dao.researcher_dao import ResearcherDao
from models.researcher import Researcher


class ResearcherRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.dao: ResearcherDao = ResearcherDao(pool)

    def remove_all(self) -> int:
        sql = """
        DELETE FROM researcher
        """
        return self.dao.execute(sql)

    def add(
        self,
        full_name: str,
        lattes_id: str,
        citation_name: str | None = None,
        orcid: str | None = None,
        nationality: str | None = None,
        birth_country: str | None = None,
        birth_state: str | None = None,
        update_date: str | None = None,
    ) -> int:
        sql = """
        INSERT INTO researcher
        (
            full_name,
            lattes_id,
            citation_name,
            orcid,
            nationality,
            birth_country,
            birth_state,
            update_date
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.dao.insert_and_return_id(
            sql,
            (
                full_name,
                lattes_id,
                citation_name,
                orcid,
                nationality,
                birth_country,
                birth_state,
                update_date,
            ),
        )

    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM researcher
        """
        count = self.dao.fetch_value(sql)
        return count if count is not None else 0

    def get_by_full_name(self, full_name: str) -> Researcher | None:
        sql = """
        SELECT
            id,
            full_name,
            lattes_id,
            citation_name,
            orcid,
            nationality,
            birth_country,
            birth_state,
            update_date
        FROM researcher
        WHERE full_name = %s
        """
        return self.dao.fetch_one(sql, (full_name,), row_factory=class_row(Researcher))
