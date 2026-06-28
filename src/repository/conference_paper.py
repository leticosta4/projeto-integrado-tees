from psycopg.rows import class_row
from psycopg import sql
from psycopg_pool import ConnectionPool

from models.conference_paper import ConferencePaper
from repository.crud import get_by_id, list_all, patch_by_id, remove_by_id


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


    def _normalize_title(self, title: str) -> str:
        return " ".join(title.strip().lower().split())


    def _find_existing_id(
        self,
        title: str,
        year: int | None,
        doi: str | None,
        event_name: str | None,
        proceedings_title: str | None,
        isbn: str | None,
    ) -> int | None:
        normalized_title = self._normalize_title(title)

        if doi:
            sql_query = """
            SELECT id
            FROM conference_paper
            WHERE lower(btrim(doi)) = lower(btrim(%s))
            LIMIT 1
            """
            values = (doi,)
        else:
            sql_query = """
            SELECT id
            FROM conference_paper
            WHERE normalized_title = %s
                AND year IS NOT DISTINCT FROM %s
                AND coalesce(lower(btrim(event_name)), '') = coalesce(lower(btrim(%s)), '')
                AND coalesce(lower(btrim(proceedings_title)), '') = coalesce(lower(btrim(%s)), '')
                AND coalesce(isbn, '') = coalesce(%s, '')
                AND nullif(btrim(coalesce(doi, '')), '') IS NULL
            LIMIT 1
            """
            values = (
                normalized_title,
                year,
                event_name,
                proceedings_title,
                isbn,
            )

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query, values)
                row = cur.fetchone()
                return row[0] if row else None


    def _add_researcher_link(
        self,
        conference_paper_id: int,
        researcher_id: int,
        matched_by: str,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
    ) -> None:
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
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
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
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> int:
        existing_id = self._find_existing_id(
            title,
            year,
            doi,
            event_name,
            proceedings_title,
            isbn,
        )
        link_matched_by = matched_by or ("doi" if doi else "normalized_title_year_event")

        if existing_id is not None:
            self._add_researcher_link(
                existing_id,
                researcher_id,
                link_matched_by,
                author_order,
                role,
                source,
            )
            return existing_id

        normalized_title = self._normalize_title(title)
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
            last_page,
            normalized_title
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        normalized_title,
                    ),
                )
                row = cur.fetchone()
                conference_paper_id = row[0] if row else 0

        if conference_paper_id:
            self._add_researcher_link(
                conference_paper_id,
                researcher_id,
                link_matched_by,
                author_order,
                role,
                source,
            )

        return conference_paper_id


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


    def count_researcher_links(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM conference_paper_researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0


    def get_by_researcher_id(self, researcher_id: int) -> list[ConferencePaper]:
        return self._list_all_by_researcher(researcher_id, {})


    def _list_all_by_researcher(
        self,
        researcher_id: int,
        filters: dict[str, object],
    ) -> list[ConferencePaper]:
        allowed_filters = set(CONFERENCE_PAPER_COLUMNS) - {"researcher_id"}
        conditions: list[sql.Composable] = [sql.SQL("cpr.researcher_id = %s")]
        values: list[object] = [researcher_id]

        for field, value in filters.items():
            if field not in allowed_filters or value is None or value == "":
                continue

            if isinstance(value, str):
                conditions.append(
                    sql.SQL("cp.{} ILIKE %s").format(sql.Identifier(field))
                )
                values.append(f"%{value}%")
            else:
                conditions.append(
                    sql.SQL("cp.{} = %s").format(sql.Identifier(field))
                )
                values.append(value)

        query = sql.SQL("""
        SELECT {}
        FROM conference_paper cp
        JOIN conference_paper_researcher cpr
            ON cpr.conference_paper_id = cp.id
        WHERE {}
        ORDER BY cp.id
        """).format(
            sql.SQL(", ").join(
                sql.SQL("cp.{}").format(sql.Identifier(column))
                for column in CONFERENCE_PAPER_COLUMNS
            ),
            sql.SQL(" AND ").join(conditions),
        )

        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(ConferencePaper)) as cur:
                _ = cur.execute(query, values)
                return cur.fetchall()


    def list_all(
        self,
        filters: dict[str, object] | None = None,
    ) -> list[ConferencePaper]:
        filters = filters or {}
        researcher_id = filters.get("researcher_id")

        if researcher_id is not None and researcher_id != "":
            try:
                return self._list_all_by_researcher(
                    int(str(researcher_id)),
                    {
                        key: value
                        for key, value in filters.items()
                        if key != "researcher_id"
                    },
                )
            except (TypeError, ValueError):
                return []

        return list_all(
            self.pool,
            "conference_paper",
            CONFERENCE_PAPER_COLUMNS,
            ConferencePaper,
            filters,
        )


    def get_by_id(self, conference_paper_id: int) -> ConferencePaper | None:
        return get_by_id(
            self.pool,
            "conference_paper",
            CONFERENCE_PAPER_COLUMNS,
            ConferencePaper,
            conference_paper_id,
        )

    def patch(
        self,
        conference_paper_id: int,
        data: dict[str, object],
    ) -> ConferencePaper | None:
        return patch_by_id(
            self.pool,
            "conference_paper",
            CONFERENCE_PAPER_COLUMNS,
            ConferencePaper,
            conference_paper_id,
            data,
        )

    def remove_by_id(self, conference_paper_id: int) -> int:
        return remove_by_id(self.pool, "conference_paper", conference_paper_id)

    def get_by_researcher_id(self, researcher_id: int) -> list[ConferencePaper]:
        return self._list_all_by_researcher(researcher_id, {})
