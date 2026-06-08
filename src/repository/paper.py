from psycopg.rows import class_row
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
            last_page,
            title_embeddings
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    ),
                )
                row = cur.fetchone()
                return row[0] if row else 0

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

    def list_all(self, filters: dict[str, object] | None = None) -> list[Paper]:
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
