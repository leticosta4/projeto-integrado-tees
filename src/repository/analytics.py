from typing import Any, LiteralString, cast

from psycopg_pool import ConnectionPool


class AnalyticsRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def summary(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> dict[str, Any]:
        area_like = self._area_like(area)
        sql = f"""
        WITH publication_rows AS ({self._publication_rows_cte()}),
        filtered AS (
            SELECT *
            FROM publication_rows
            WHERE {self._filters_condition()}
        ),
        production_by_type AS (
            SELECT
                type,
                COUNT(DISTINCT publication_key) AS unique_publications,
                COUNT(*) AS authorships,
                COUNT(DISTINCT publication_key) FILTER (WHERE author_count > 1)
                    AS collaborative_publications
            FROM filtered
            GROUP BY type
        )
        SELECT jsonb_build_object(
            'total_researchers', (
                SELECT COUNT(*)
                FROM researcher r
                WHERE (
                    %s::text IS NULL
                    OR EXISTS (
                        SELECT 1
                        FROM research_area ra
                        WHERE ra.researcher_id = r.id
                            AND {self._area_text_condition("ra", "%s")}
                    )
                )
            ),
            'total_unique_publications', COALESCE((
                SELECT COUNT(DISTINCT publication_key)
                FROM filtered
            ), 0),
            'total_authorships', COALESCE((
                SELECT COUNT(*)
                FROM filtered
            ), 0),
            'collaborative_publications', COALESCE((
                SELECT COUNT(DISTINCT publication_key)
                FROM filtered
                WHERE author_count > 1
            ), 0),
            'productions_by_type', COALESCE((
                SELECT jsonb_object_agg(
                    type,
                    jsonb_build_object(
                        'unique_publications', unique_publications,
                        'authorships', authorships,
                        'collaborative_publications', collaborative_publications
                    )
                    ORDER BY type
                )
                FROM production_by_type
            ), '{{}}'::jsonb),
            'papers_without_doi', (
                SELECT COUNT(*)
                FROM papers p
                WHERE (p.doi IS NULL OR btrim(p.doi) = '')
            ),
            'conference_papers_without_doi', (
                SELECT COUNT(*)
                FROM conference_paper cp
                WHERE (cp.doi IS NULL OR btrim(cp.doi) = '')
            ),
            'duplicate_doi_groups', (
                SELECT COUNT(*)
                FROM (
                    SELECT lower(btrim(doi)) AS doi
                    FROM papers
                    WHERE doi IS NOT NULL AND btrim(doi) <> ''
                    GROUP BY lower(btrim(doi))
                    HAVING COUNT(*) > 1
                    UNION ALL
                    SELECT lower(btrim(doi)) AS doi
                    FROM conference_paper
                    WHERE doi IS NOT NULL AND btrim(doi) <> ''
                    GROUP BY lower(btrim(doi))
                    HAVING COUNT(*) > 1
                ) duplicates
            ),
            'average_curriculum_update_year', (
                SELECT ROUND(AVG(substring(update_date from '([0-9]{{4}})')::numeric), 1)
                FROM researcher
                WHERE update_date ~ '[0-9]{{4}}'
            )
        ) AS data
        """
        return self._fetch_json(
            sql,
            [
                year_from,
                year_from,
                year_to,
                year_to,
                list(types),
                area,
                area_like,
                area,
                area_like,
            ],
        )


    def publications_by_year(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> list[dict[str, Any]]:
        area_like = self._area_like(area)
        sql = f"""
        WITH publication_rows AS ({self._publication_rows_cte()}),
        filtered AS (
            SELECT *
            FROM publication_rows
            WHERE year IS NOT NULL
                AND {self._filters_condition()}
        )
        SELECT
            year,
            type,
            COUNT(DISTINCT publication_key) AS unique_publications,
            COUNT(*) AS authorships,
            COUNT(DISTINCT publication_key) FILTER (WHERE author_count > 1)
                AS collaborative_publications
        FROM filtered
        GROUP BY year, type
        ORDER BY year, type
        """
        return self._fetch_all(
            sql,
            [year_from, year_from, year_to, year_to, list(types), area, area_like],
        )


    def publications_by_area(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int | None = 10,
    ) -> list[dict[str, Any]]:
        area_like = self._area_like(area)
        limit_clause = "LIMIT %s" if limit is not None else ""
        sql = f"""
        WITH publication_rows AS ({self._publication_rows_cte()}),
        filtered AS (
            SELECT *
            FROM publication_rows
            WHERE {self._filters_condition()}
        )
        SELECT
            COALESCE(ra.area, ra.major_area, ra.sub_area, ra.specialty, 'Area nao informada')
                AS area,
            COUNT(DISTINCT filtered.publication_key) AS unique_publications,
            COUNT(*) AS authorships,
            COUNT(DISTINCT filtered.publication_key) FILTER (WHERE filtered.author_count > 1)
                AS collaborative_publications
        FROM filtered
        LEFT JOIN research_area ra ON ra.researcher_id = filtered.researcher_id
        GROUP BY COALESCE(ra.area, ra.major_area, ra.sub_area, ra.specialty, 'Area nao informada')
        ORDER BY unique_publications DESC, authorships DESC, area
        {limit_clause}
        """
        params = [year_from, year_from, year_to, year_to, list(types), area, area_like]
        if limit is not None:
            params.append(limit)
        return self._fetch_all(sql, params)


    def top_researchers(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int | None = 8,
    ) -> list[dict[str, Any]]:
        area_like = self._area_like(area)
        limit_clause = "LIMIT %s" if limit is not None else ""
        sql = f"""
        WITH publication_rows AS ({self._publication_rows_cte()}),
        filtered AS (
            SELECT *
            FROM publication_rows
            WHERE {self._filters_condition()}
        )
        SELECT
            r.id AS researcher_id,
            r.full_name,
            COUNT(DISTINCT filtered.publication_key) AS unique_publications,
            COUNT(*) AS authorships,
            COUNT(DISTINCT filtered.publication_key) FILTER (WHERE filtered.author_count > 1)
                AS collaborative_publications
        FROM filtered
        JOIN researcher r ON r.id = filtered.researcher_id
        GROUP BY r.id, r.full_name
        ORDER BY authorships DESC, unique_publications DESC, r.full_name
        {limit_clause}
        """
        params = [year_from, year_from, year_to, year_to, list(types), area, area_like]
        if limit is not None:
            params.append(limit)
        return self._fetch_all(sql, params)


    def coauthor_network(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int = 50,
    ) -> dict[str, list[dict[str, Any]]]:
        area_like = self._area_like(area)
        sql = f"""
        WITH publication_rows AS ({self._publication_rows_cte()}),
        filtered AS (
            SELECT *
            FROM publication_rows
            WHERE type IN ('paper', 'conference_paper')
                AND {self._filters_condition()}
        ),
        pairs AS (
            SELECT
                left_row.researcher_id AS source,
                right_row.researcher_id AS target,
                COUNT(DISTINCT left_row.publication_key) AS weight
            FROM filtered left_row
            JOIN filtered right_row
                ON right_row.publication_key = left_row.publication_key
                AND right_row.researcher_id > left_row.researcher_id
            GROUP BY left_row.researcher_id, right_row.researcher_id
        ),
        limited_pairs AS (
            SELECT *
            FROM pairs
            ORDER BY weight DESC, source, target
            LIMIT %s
        ),
        nodes AS (
            SELECT DISTINCT researcher_id
            FROM (
                SELECT source AS researcher_id FROM limited_pairs
                UNION
                SELECT target AS researcher_id FROM limited_pairs
            ) researcher_ids
        )
        SELECT jsonb_build_object(
            'nodes', COALESCE((
                SELECT jsonb_agg(
                    jsonb_build_object('id', r.id, 'label', r.full_name)
                    ORDER BY r.full_name
                )
                FROM nodes
                JOIN researcher r ON r.id = nodes.researcher_id
            ), '[]'::jsonb),
            'edges', COALESCE((
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'source', source,
                        'target', target,
                        'weight', weight
                    )
                    ORDER BY weight DESC, source, target
                )
                FROM limited_pairs
            ), '[]'::jsonb)
        ) AS data
        """
        return self._fetch_json(
            sql,
            [year_from, year_from, year_to, year_to, list(types), area, area_like, limit],
        )


    def _publication_rows_cte(self) -> str:
        return """
            SELECT
                'paper:' || p.id AS publication_key,
                'paper' AS type,
                p.id AS publication_id,
                p.title,
                p.year,
                pr.researcher_id,
                author_counts.author_count
            FROM papers p
            JOIN paper_researcher pr ON pr.paper_id = p.id
            JOIN (
                SELECT paper_id, COUNT(*) AS author_count
                FROM paper_researcher
                GROUP BY paper_id
            ) author_counts ON author_counts.paper_id = p.id

            UNION ALL

            SELECT
                'conference_paper:' || cp.id AS publication_key,
                'conference_paper' AS type,
                cp.id AS publication_id,
                cp.title,
                cp.year,
                cpr.researcher_id,
                author_counts.author_count
            FROM conference_paper cp
            JOIN conference_paper_researcher cpr ON cpr.conference_paper_id = cp.id
            JOIN (
                SELECT conference_paper_id, COUNT(*) AS author_count
                FROM conference_paper_researcher
                GROUP BY conference_paper_id
            ) author_counts ON author_counts.conference_paper_id = cp.id

            UNION ALL

            SELECT
                'advising:' || a.id AS publication_key,
                'advising' AS type,
                a.id AS publication_id,
                a.title,
                a.year,
                a.researcher_id,
                1 AS author_count
            FROM advising a
        """


    def _filters_condition(self) -> str:
        return f"""
            (%s::integer IS NULL OR year >= %s::integer)
            AND (%s::integer IS NULL OR year <= %s::integer)
            AND type = ANY(%s::text[])
            AND (
                %s::text IS NULL
                OR EXISTS (
                    SELECT 1
                    FROM research_area ra_filter
                    WHERE ra_filter.researcher_id = publication_rows.researcher_id
                        AND {self._area_text_condition("ra_filter", "%s")}
                )
            )
        """


    def _area_text_condition(self, alias: str, placeholder: str) -> str:
        return f"""
            concat_ws(
                ' ',
                {alias}.major_area,
                {alias}.area,
                {alias}.sub_area,
                {alias}.specialty
            ) ILIKE {placeholder}
        """


    def _area_like(self, area: str | None) -> str | None:
        return f"%{area}%" if area else None


    def _fetch_all(self, query: str, values: list[object]) -> list[dict[str, Any]]:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(cast(LiteralString, query), tuple(values))
                if cur.description is None:
                    return []

                columns = [column.name for column in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]


    def _fetch_json(self, query: str, values: list[object]) -> dict[str, Any]:
        rows = self._fetch_all(query, values)
        return rows[0]["data"] if rows else {}
