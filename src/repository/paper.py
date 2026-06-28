from psycopg.rows import class_row
from psycopg import sql
from psycopg_pool import ConnectionPool

from models.paper import Paper
from repository.crud import get_by_id, list_all, patch_by_id, remove_by_id


PAPER_COLUMNS = [
    "id",
    "title",
    "researcher_id",
    "year",
    "doi",
    "language",
    "nature",
    "country",
    "journal",
    "issn",
    "volume",
    "issue",
    "first_page",
    "last_page",
    "title_embeddings",
]


class PaperRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def _normalize_title(self, title: str) -> str:
        return " ".join(title.strip().lower().split())


    def _find_existing_id(
        self,
        title: str,
        year: int | None,
        doi: str | None,
        journal: str | None,
        issn: str | None,
    ) -> int | None:
        normalized_title = self._normalize_title(title)

        if doi:
            sql_query = """
            SELECT id
            FROM papers
            WHERE lower(btrim(doi)) = lower(btrim(%s))
            LIMIT 1
            """
            values = (doi,)
        else:
            sql_query = """
            SELECT id
            FROM papers
            WHERE normalized_title = %s
                AND year IS NOT DISTINCT FROM %s
                AND coalesce(lower(btrim(journal)), '') = coalesce(lower(btrim(%s)), '')
                AND coalesce(issn, '') = coalesce(%s, '')
                AND nullif(btrim(coalesce(doi, '')), '') IS NULL
            LIMIT 1
            """
            values = (normalized_title, year, journal, issn)

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql_query, values)
                row = cur.fetchone()
                return row[0] if row else None


    def _add_researcher_link(
        self,
        paper_id: int,
        researcher_id: int,
        matched_by: str,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
    ) -> None:
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
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
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


    def remove_all(self) -> int:
        sql = """
        DELETE FROM papers
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                return cur.rowcount


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
        title_embeddings: list[float] | None = None,
        author_order: int | None = None,
        role: str | None = "author",
        source: str | None = "lattes_xml",
        matched_by: str | None = None,
    ) -> int:
        existing_id = self._find_existing_id(title, year, doi, journal, issn)
        link_matched_by = matched_by or ("doi" if doi else "normalized_title_year_journal")

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
            last_page,
            title_embeddings,
            normalized_title
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
                        title_embeddings,
                        normalized_title,
                    ),
                )
                row = cur.fetchone()
                paper_id = row[0] if row else 0

        if paper_id:
            self._add_researcher_link(
                paper_id,
                researcher_id,
                link_matched_by,
                author_order,
                role,
                source,
            )

        return paper_id


    def count(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM papers
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0


    def count_researcher_links(self) -> int:
        sql = """
        SELECT COUNT(*)
        FROM paper_researcher
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else 0


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
            last_page,
            title_embeddings
        FROM papers
        WHERE title = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(sql, (title,))
                return cur.fetchone()


    def search(
        self,
        query: str,
        embedding: list[float],
        limit: int = 10,
    ) -> list[tuple[Paper, float]]:
        sql = """
        WITH fts_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY ts_rank_cd(to_tsvector('portuguese', title), plainto_tsquery('portuguese', %s)) DESC) as rank
            FROM papers
            WHERE to_tsvector('portuguese', title) @@ plainto_tsquery('portuguese', %s)
            LIMIT 100
        ),
        vector_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY title_embeddings <=> %s::vector) as rank
            FROM papers
            WHERE title_embeddings IS NOT NULL
            ORDER BY title_embeddings <=> %s::vector
            LIMIT 100
        )
        SELECT
            p.id,
            p.title,
            p.researcher_id,
            p.year,
            p.doi,
            p.language,
            p.nature,
            p.country,
            p.journal,
            p.issn,
            p.volume,
            p.issue,
            p.first_page,
            p.last_page,
            p.title_embeddings,
            COALESCE(1.0 / (60 + fts.rank), 0.0) +
            COALESCE(1.0 / (60 + vec.rank), 0.0) AS rrf_score
        FROM fts_search fts
        FULL OUTER JOIN vector_search vec ON fts.id = vec.id
        JOIN papers p ON p.id = COALESCE(fts.id, vec.id)
        ORDER BY rrf_score DESC
        LIMIT %s
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, (query, query, embedding, embedding, limit))
                results = []
                for row in cur.fetchall():
                    # We need to manually map to Paper model because of the extra rrf_score column
                    # Or use a custom row factory, but this is simpler for now
                    paper_data = list(row[:-1])
                    rrf_score = row[-1]

                    # Create Paper object manually to handle title_embeddings deserialization
                    # (since we are not using class_row(Paper) here)
                    # Actually, I should use Paper.model_validate or similar if possible
                    # but since I added a field_validator to Paper, I can use it.

                    paper = Paper(
                        id=paper_data[0],
                        title=paper_data[1],
                        researcher_id=paper_data[2],
                        year=paper_data[3],
                        doi=paper_data[4],
                        language=paper_data[5],
                        nature=paper_data[6],
                        country=paper_data[7],
                        journal=paper_data[8],
                        issn=paper_data[9],
                        volume=paper_data[10],
                        issue=paper_data[11],
                        first_page=paper_data[12],
                        last_page=paper_data[13],
                        title_embeddings=paper_data[14]
                    )
                    results.append((paper, rrf_score))
                return results
    def _list_all_by_researcher(
        self,
        researcher_id: int,
        filters: dict[str, object],
    ) -> list[Paper]:
        allowed_filters = set(PAPER_COLUMNS) - {"researcher_id"}
        conditions: list[sql.Composable] = [sql.SQL("pr.researcher_id = %s")]
        values: list[object] = [researcher_id]

        for field, value in filters.items():
            if field not in allowed_filters or value is None or value == "":
                continue

            if isinstance(value, str):
                conditions.append(
                    sql.SQL("p.{} ILIKE %s").format(sql.Identifier(field))
                )
                values.append(f"%{value}%")
            else:
                conditions.append(
                    sql.SQL("p.{} = %s").format(sql.Identifier(field))
                )
                values.append(value)

        query = sql.SQL("""
        SELECT {}
        FROM papers p
        JOIN paper_researcher pr ON pr.paper_id = p.id
        WHERE {}
        ORDER BY p.id
        """).format(
            sql.SQL(", ").join(
                sql.SQL("p.{}").format(sql.Identifier(column))
                for column in PAPER_COLUMNS
            ),
            sql.SQL(" AND ").join(conditions),
        )

        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(query, values)
                return cur.fetchall()


    def list_all(self, filters: dict[str, object] | None = None) -> list[Paper]:
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

        return list_all(self.pool, "papers", PAPER_COLUMNS, Paper, filters)


    def get_by_id(self, paper_id: int) -> Paper | None:
        return get_by_id(self.pool, "papers", PAPER_COLUMNS, Paper, paper_id)


    def patch(self, paper_id: int, data: dict[str, object]) -> Paper | None:
        return patch_by_id(self.pool, "papers", PAPER_COLUMNS, Paper, paper_id, data)


    def remove_by_id(self, paper_id: int) -> int:
        return remove_by_id(self.pool, "papers", paper_id)


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
            last_page,
            title_embeddings
        FROM papers
        WHERE title = %s
        """
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Paper)) as cur:
                _ = cur.execute(sql, (title,))
                return cur.fetchone()


    def search(
        self,
        query: str,
        embedding: list[float],
        limit: int = 10,
    ) -> list[tuple[Paper, float]]:
        sql = """
        WITH fts_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY ts_rank_cd(to_tsvector('portuguese', title), plainto_tsquery('portuguese', %s)) DESC) as rank
            FROM papers
            WHERE to_tsvector('portuguese', title) @@ plainto_tsquery('portuguese', %s)
            LIMIT 100
        ),
        vector_search AS (
            SELECT
                id,
                ROW_NUMBER() OVER (ORDER BY title_embeddings <=> %s::vector) as rank
            FROM papers
            WHERE title_embeddings IS NOT NULL
            ORDER BY title_embeddings <=> %s::vector
            LIMIT 100
        )
        SELECT
            p.id,
            p.title,
            p.researcher_id,
            p.year,
            p.doi,
            p.language,
            p.nature,
            p.country,
            p.journal,
            p.issn,
            p.volume,
            p.issue,
            p.first_page,
            p.last_page,
            p.title_embeddings,
            COALESCE(1.0 / (60 + fts.rank), 0.0) +
            COALESCE(1.0 / (60 + vec.rank), 0.0) AS rrf_score
        FROM fts_search fts
        FULL OUTER JOIN vector_search vec ON fts.id = vec.id
        JOIN papers p ON p.id = COALESCE(fts.id, vec.id)
        ORDER BY rrf_score DESC
        LIMIT %s
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, (query, query, embedding, embedding, limit))
                results = []
                for row in cur.fetchall():
                    # We need to manually map to Paper model because of the extra rrf_score column
                    # Or use a custom row factory, but this is simpler for now
                    paper_data = list(row[:-1])
                    rrf_score = row[-1]

                    # Create Paper object manually to handle title_embeddings deserialization
                    # (since we are not using class_row(Paper) here)
                    # Actually, I should use Paper.model_validate or similar if possible
                    # but since I added a field_validator to Paper, I can use it.

                    paper = Paper(
                        id=paper_data[0],
                        title=paper_data[1],
                        researcher_id=paper_data[2],
                        year=paper_data[3],
                        doi=paper_data[4],
                        language=paper_data[5],
                        nature=paper_data[6],
                        country=paper_data[7],
                        journal=paper_data[8],
                        issn=paper_data[9],
                        volume=paper_data[10],
                        issue=paper_data[11],
                        first_page=paper_data[12],
                        last_page=paper_data[13],
                        title_embeddings=paper_data[14]
                    )
                    results.append((paper, rrf_score))
                return results

