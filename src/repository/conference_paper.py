from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.conference_paper import ConferencePaper
from repository.crud import list_all


CONFERENCE_PAPER_COLUMNS = [
    "id",
    "researcher_id",
    "title",
    "year",
    "nature",
    "country",
    "language",
    "doi",
    "event_name",
    "event_city",
    "event_year",
    "event_classification",
    "proceedings_title",
    "isbn",
    "first_page",
    "last_page",
]


class ConferencePaperRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def remove_all(self) -> int:
        sql = """
        DELETE FROM conference_paper
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount


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
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
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
                row = cur.fetchone()
                return row[0] if row else 0


    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM conference_paper
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0

  
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
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ConferencePaper)) as cur:
                _ = cur.execute(sql, (researcher_id,))
                return cur.fetchall()


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[ConferencePaper]:
        return list_all(
            self.pool,
            "conference_paper",
            CONFERENCE_PAPER_COLUMNS,
            ConferencePaper,
            filters,
        )
    