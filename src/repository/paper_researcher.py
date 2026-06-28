from psycopg import sql
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.paper_researcher import PaperResearcher


PAPER_RESEARCHER_COLUMNS = [
    "paper_id",
    "researcher_id",
    "author_order",
    "role",
    "source",
    "matched_by",
]


class PaperResearcherRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def add(
        self,
        paper_id: int,
        researcher_id: int,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> PaperResearcher | None:
        sql_query = """
        INSERT INTO paper_researcher
        (
            paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (paper_id, researcher_id) DO UPDATE
        SET
            author_order = coalesce(EXCLUDED.author_order, paper_researcher.author_order),
            role = coalesce(EXCLUDED.role, paper_researcher.role),
            source = coalesce(EXCLUDED.source, paper_researcher.source),
            matched_by = coalesce(EXCLUDED.matched_by, paper_researcher.matched_by)
        RETURNING
            paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(PaperResearcher)) as cur:
                _ = cur.execute(
                    sql_query,
                    (
                        paper_id,
                        researcher_id,
                        author_order,
                        role,
                        source,
                        matched_by,
                    ),
                )
                return cur.fetchone()


    def count(self) -> int:
        sql_query = """
        SELECT COUNT(*)
        FROM paper_researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query)
                row = cur.fetchone()
                return row[0] if row else 0


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[PaperResearcher]:
        allowed_filters = set(PAPER_RESEARCHER_COLUMNS)
        conditions: list[sql.Composable] = []
        values: list[object] = []

        for field, value in (filters or {}).items():
            if field not in allowed_filters or value is None or value == "":
                continue

            conditions.append(sql.SQL("{} = %s").format(sql.Identifier(field)))
            values.append(value)

        where_clause = (
            sql.SQL("WHERE ") + sql.SQL(" AND ").join(conditions)
            if conditions
            else sql.SQL("")
        )
        query = sql.SQL("""
        SELECT {}
        FROM paper_researcher
        {}
        ORDER BY paper_id, researcher_id
        """).format(
            sql.SQL(", ").join(sql.Identifier(column) for column in PAPER_RESEARCHER_COLUMNS),
            where_clause,
        )

        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(PaperResearcher)) as cur:
                _ = cur.execute(query, values)
                return cur.fetchall()


    def get_by_paper_id(self, paper_id: int) -> list[PaperResearcher]:
        return self.list_all({"paper_id": paper_id})


    def get_by_researcher_id(self, researcher_id: int) -> list[PaperResearcher]:
        return self.list_all({"researcher_id": researcher_id})


    def get(
        self,
        paper_id: int,
        researcher_id: int,
    ) -> PaperResearcher | None:
        links = self.list_all(
            {
                "paper_id": paper_id,
                "researcher_id": researcher_id,
            }
        )
        return links[0] if links else None


    def remove(
        self,
        paper_id: int,
        researcher_id: int,
    ) -> int:
        sql_query = """
        DELETE FROM paper_researcher
        WHERE paper_id = %s
            AND researcher_id = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query, (paper_id, researcher_id))
                return cur.rowcount
