from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.researcher import Researcher
from repository.crud import list_all


RESEARCHER_COLUMNS = [
    "id",
    "full_name",
    "lattes_id",
    "citation_name",
    "orcid",
    "nationality",
    "birth_country",
    "birth_state",
    "update_date",
]


class ResearcherRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def remove_all(self) -> int:
        sql = """
        DELETE FROM researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount


    def add(
        self,
        full_name: str,
        filename: str,
        filehash: str,
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
            filename,
            filehash,
            lattes_id,
            citation_name,
            orcid,
            nationality,
            birth_country,
            birth_state,
            update_date
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(
                    sql,
                    (
                        full_name,
                        filename,
                        filehash,
                        lattes_id,
                        citation_name,
                        orcid,
                        nationality,
                        birth_country,
                        birth_state,
                        update_date,
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0


    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0


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
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Researcher)) as cur:
                _ = cur.execute(sql, (full_name,))
                return cur.fetchone()


    def select_filehash_exists(self, filehash: str) -> str | None:
        sql = """
        SELECT filehash
        FROM researcher
        WHERE filehash = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, (filehash,))
                row = cur.fetchone()
                return row[0] if row else None


    def list_all(self, filters: dict[str, object] | None = None) -> list[Researcher]:
        return list_all(
            self.pool,
            "researcher",
            RESEARCHER_COLUMNS,
            Researcher,
            filters,
        )
    