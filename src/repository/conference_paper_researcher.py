from psycopg import sql
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from models.conference_paper_researcher import ConferencePaperResearcher


CONFERENCE_PAPER_RESEARCHER_COLUMNS = [
    "conference_paper_id",
    "researcher_id",
    "author_order",
    "role",
    "source",
    "matched_by",
]


class ConferencePaperResearcherRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def add(
        self,
        conference_paper_id: int,
        researcher_id: int,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> ConferencePaperResearcher | None:
        sql_query = """
        INSERT INTO conference_paper_researcher
        (
            conference_paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (conference_paper_id, researcher_id) DO UPDATE
        SET
            author_order = coalesce(EXCLUDED.author_order, conference_paper_researcher.author_order),
            role = coalesce(EXCLUDED.role, conference_paper_researcher.role),
            source = coalesce(EXCLUDED.source, conference_paper_researcher.source),
            matched_by = coalesce(EXCLUDED.matched_by, conference_paper_researcher.matched_by)
        RETURNING
            conference_paper_id,
            researcher_id,
            author_order,
            role,
            source,
            matched_by
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ConferencePaperResearcher)) as cur:
                _ = cur.execute(
                    sql_query,
                    (
                        conference_paper_id,
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
        FROM conference_paper_researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query)
                row = cur.fetchone()
                return row[0] if row else 0


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[ConferencePaperResearcher]:
        allowed_filters = set(CONFERENCE_PAPER_RESEARCHER_COLUMNS)
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
        FROM conference_paper_researcher
        {}
        ORDER BY conference_paper_id, researcher_id
        """).format(
            sql.SQL(", ").join(
                sql.Identifier(column)
                for column in CONFERENCE_PAPER_RESEARCHER_COLUMNS
            ),
            where_clause,
        )

        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ConferencePaperResearcher)) as cur:
                _ = cur.execute(query, values)
                return cur.fetchall()


    def get_by_conference_paper_id(
        self,
        conference_paper_id: int,
    ) -> list[ConferencePaperResearcher]:
        return self.list_all({"conference_paper_id": conference_paper_id})


    def get_by_researcher_id(
        self,
        researcher_id: int,
    ) -> list[ConferencePaperResearcher]:
        return self.list_all({"researcher_id": researcher_id})


    def get(
        self,
        conference_paper_id: int,
        researcher_id: int,
    ) -> ConferencePaperResearcher | None:
        links = self.list_all(
            {
                "conference_paper_id": conference_paper_id,
                "researcher_id": researcher_id,
            }
        )
        return links[0] if links else None


    def remove(
        self,
        conference_paper_id: int,
        researcher_id: int,
    ) -> int:
        sql_query = """
        DELETE FROM conference_paper_researcher
        WHERE conference_paper_id = %s
            AND researcher_id = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query, (conference_paper_id, researcher_id))
                return cur.rowcount
