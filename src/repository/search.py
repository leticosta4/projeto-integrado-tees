import re
import unicodedata
from typing import Any

from psycopg_pool import ConnectionPool


class SearchRepository:
    QUERY_SYNONYMS = {
        "ia": ("inteligencia artificial", "artificial intelligence", "ai"),
        "ai": ("inteligencia artificial", "artificial intelligence", "ia"),
        "inteligencia": ("inteligencia artificial", "intelligence", "ai", "ia"),
        "intelligence": ("inteligencia", "inteligencia artificial", "ai", "ia"),
        "aprendizagem": ("learning", "machine learning"),
        "learning": ("aprendizagem", "machine learning"),
    }

    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool


    def search(
        self,
        query: str,
        types: set[str],
        result_kinds: set[str],
        limit: int,
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        researcher_id: int | None = None,
    ) -> list[dict[str, Any]]:
        subqueries: list[str] = []
        values: list[Any] = []
        text_values = self._text_values(query)
        area_like = f"%{area}%" if area else None

        if "publications" in result_kinds and "paper" in types:
            subqueries.append(self._paper_query())
            values.extend(
                self._text_params(text_values)
                + [
                    year_from,
                    year_from,
                    year_to,
                    year_to,
                    researcher_id,
                    researcher_id,
                    area_like,
                    area_like,
                ]
            )

        if "publications" in result_kinds and "conference_paper" in types:
            subqueries.append(self._conference_paper_query())
            values.extend(
                self._text_params(text_values)
                + [
                    year_from,
                    year_from,
                    year_to,
                    year_to,
                    researcher_id,
                    researcher_id,
                    area_like,
                    area_like,
                ]
            )

        if "publications" in result_kinds and "advising" in types:
            subqueries.append(self._advising_query())
            values.extend(
                self._text_params(text_values)
                + [
                    year_from,
                    year_from,
                    year_to,
                    year_to,
                    researcher_id,
                    researcher_id,
                    area_like,
                    area_like,
                ]
            )

        if "researchers" in result_kinds:
            subqueries.append(self._researcher_query())
            values.extend(
                self._text_params(text_values)
                + [
                    researcher_id,
                    researcher_id,
                    area_like,
                    area_like,
                ]
            )

        if not subqueries:
            return []

        sql = f"""
        SELECT *
        FROM (
            {" UNION ALL ".join(subqueries)}
        ) results
        ORDER BY score DESC, title
        LIMIT %s
        """
        values.append(limit)

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, values)
                columns = [column.name for column in cur.description]
                return [
                    dict(zip(columns, row))
                    for row in cur.fetchall()
                ]


    def _text_values(self, query: str) -> dict[str, object]:
        normalized_query = self._normalize(query)
        tokens = [
            token
            for token in re.findall(r"[a-z0-9]+", normalized_query)
            if len(token) >= 3
        ]
        expanded_terms = [query, normalized_query]

        for token in tokens:
            expanded_terms.append(token)
            expanded_terms.extend(self.QUERY_SYNONYMS.get(token, ()))

        unique_terms = list(dict.fromkeys(term.strip() for term in expanded_terms if term.strip()))
        ts_query = " OR ".join(self._websearch_term(term) for term in unique_terms)
        phrase_like = f"%{query}%"
        partial_likes = [f"%{term}%" for term in unique_terms]

        return {
            "ts_query": ts_query,
            "phrase_like": phrase_like,
            "partial_likes": partial_likes,
        }


    def _text_params(self, text_values: dict[str, object]) -> list[object]:
        return [
            text_values["ts_query"],
            text_values["phrase_like"],
            text_values["partial_likes"],
            text_values["ts_query"],
            text_values["phrase_like"],
            text_values["partial_likes"],
        ]


    def _websearch_term(self, term: str) -> str:
        return f'"{term}"' if " " in term else term


    def _normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        return ascii_value.lower()


    def _score_expression(self) -> str:
        return """
            ts_rank_cd(
                to_tsvector('portuguese', immutable_unaccent(search.text)),
                websearch_to_tsquery('portuguese', immutable_unaccent(%s))
            )
            + CASE
                WHEN immutable_unaccent(lower(search.text))
                    ILIKE immutable_unaccent(lower(%s))
                THEN 0.10
                ELSE 0
            END
            + CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM unnest(%s::text[]) AS pattern(value)
                    WHERE immutable_unaccent(lower(search.text))
                        ILIKE immutable_unaccent(lower(pattern.value))
                )
                THEN 0.03
                ELSE 0
            END AS score
        """


    def _text_match_condition(self) -> str:
        return """
            (
                to_tsvector('portuguese', immutable_unaccent(search.text))
                    @@ websearch_to_tsquery('portuguese', immutable_unaccent(%s))
                OR immutable_unaccent(lower(search.text))
                    ILIKE immutable_unaccent(lower(%s))
                OR EXISTS (
                    SELECT 1
                    FROM unnest(%s::text[]) AS pattern(value)
                    WHERE immutable_unaccent(lower(search.text))
                        ILIKE immutable_unaccent(lower(pattern.value))
                )
            )
        """


    def _area_filter_condition(self) -> str:
        return """
            (
                %s::text IS NULL
                OR immutable_unaccent(lower(search.area_text))
                    ILIKE immutable_unaccent(lower(%s))
            )
        """


    def _paper_query(self) -> str:
        return f"""
        SELECT
            'paper' AS result_type,
            p.id AS id,
            p.title AS title,
            p.year AS year,
            p.researcher_id AS researcher_id,
            jsonb_build_object(
                'id', primary_researcher.id,
                'full_name', primary_researcher.full_name
            ) AS primary_researcher,
            COALESCE((
                SELECT jsonb_agg(
                    jsonb_build_object('id', r.id, 'full_name', r.full_name)
                    ORDER BY r.full_name
                )
                FROM paper_researcher pr
                JOIN researcher r ON r.id = pr.researcher_id
                WHERE pr.paper_id = p.id
            ), '[]'::jsonb) AS authors,
            COALESCE((
                SELECT jsonb_agg(DISTINCT jsonb_build_object(
                    'major_area', ra.major_area,
                    'area', ra.area,
                    'sub_area', ra.sub_area,
                    'specialty', ra.specialty
                ))
                FROM paper_researcher pr
                JOIN research_area ra ON ra.researcher_id = pr.researcher_id
                WHERE pr.paper_id = p.id
            ), '[]'::jsonb) AS areas,
            jsonb_build_object(
                'doi', p.doi,
                'journal', p.journal,
                'nature', p.nature,
                'language', p.language,
                'country', p.country
            ) AS metadata,
            {self._score_expression()}
        FROM papers p
        JOIN researcher primary_researcher ON primary_researcher.id = p.researcher_id
        CROSS JOIN LATERAL (
            SELECT
                concat_ws(
                    ' ',
                    p.title,
                    p.doi,
                    p.journal,
                    p.issn,
                    p.nature,
                    p.language,
                    p.country,
                    primary_researcher.full_name,
                    primary_researcher.citation_name,
                    (
                        SELECT string_agg(r.full_name, ' ')
                        FROM paper_researcher pr_text
                        JOIN researcher r ON r.id = pr_text.researcher_id
                        WHERE pr_text.paper_id = p.id
                    ),
                    (
                        SELECT string_agg(
                            concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                            ' '
                        )
                        FROM paper_researcher pr_area_text
                        JOIN research_area ra ON ra.researcher_id = pr_area_text.researcher_id
                        WHERE pr_area_text.paper_id = p.id
                    )
                ) AS text,
                COALESCE((
                    SELECT string_agg(
                        concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                        ' '
                    )
                    FROM paper_researcher pr_area_text
                    JOIN research_area ra ON ra.researcher_id = pr_area_text.researcher_id
                    WHERE pr_area_text.paper_id = p.id
                ), '') AS area_text
        ) search
        WHERE {self._text_match_condition()}
            AND (%s::integer IS NULL OR p.year >= %s::integer)
            AND (%s::integer IS NULL OR p.year <= %s::integer)
            AND (
                %s::integer IS NULL
                OR EXISTS (
                    SELECT 1
                    FROM paper_researcher pr_filter
                    WHERE pr_filter.paper_id = p.id
                        AND pr_filter.researcher_id = %s
                )
            )
            AND {self._area_filter_condition()}
        """


    def _conference_paper_query(self) -> str:
        return f"""
        SELECT
            'conference_paper' AS result_type,
            cp.id AS id,
            cp.title AS title,
            cp.year AS year,
            cp.researcher_id AS researcher_id,
            jsonb_build_object(
                'id', primary_researcher.id,
                'full_name', primary_researcher.full_name
            ) AS primary_researcher,
            COALESCE((
                SELECT jsonb_agg(
                    jsonb_build_object('id', r.id, 'full_name', r.full_name)
                    ORDER BY r.full_name
                )
                FROM conference_paper_researcher cpr
                JOIN researcher r ON r.id = cpr.researcher_id
                WHERE cpr.conference_paper_id = cp.id
            ), '[]'::jsonb) AS authors,
            COALESCE((
                SELECT jsonb_agg(DISTINCT jsonb_build_object(
                    'major_area', ra.major_area,
                    'area', ra.area,
                    'sub_area', ra.sub_area,
                    'specialty', ra.specialty
                ))
                FROM conference_paper_researcher cpr
                JOIN research_area ra ON ra.researcher_id = cpr.researcher_id
                WHERE cpr.conference_paper_id = cp.id
            ), '[]'::jsonb) AS areas,
            jsonb_build_object(
                'doi', cp.doi,
                'event_name', cp.event_name,
                'event_city', cp.event_city,
                'proceedings_title', cp.proceedings_title,
                'nature', cp.nature,
                'language', cp.language,
                'country', cp.country
            ) AS metadata,
            {self._score_expression()}
        FROM conference_paper cp
        JOIN researcher primary_researcher ON primary_researcher.id = cp.researcher_id
        CROSS JOIN LATERAL (
            SELECT
                concat_ws(
                    ' ',
                    cp.title,
                    cp.doi,
                    cp.event_name,
                    cp.event_city,
                    cp.event_classification,
                    cp.proceedings_title,
                    cp.isbn,
                    cp.nature,
                    cp.language,
                    cp.country,
                    primary_researcher.full_name,
                    primary_researcher.citation_name,
                    (
                        SELECT string_agg(r.full_name, ' ')
                        FROM conference_paper_researcher cpr_text
                        JOIN researcher r ON r.id = cpr_text.researcher_id
                        WHERE cpr_text.conference_paper_id = cp.id
                    ),
                    (
                        SELECT string_agg(
                            concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                            ' '
                        )
                        FROM conference_paper_researcher cpr_area_text
                        JOIN research_area ra ON ra.researcher_id = cpr_area_text.researcher_id
                        WHERE cpr_area_text.conference_paper_id = cp.id
                    )
                ) AS text,
                COALESCE((
                    SELECT string_agg(
                        concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                        ' '
                    )
                    FROM conference_paper_researcher cpr_area_text
                    JOIN research_area ra ON ra.researcher_id = cpr_area_text.researcher_id
                    WHERE cpr_area_text.conference_paper_id = cp.id
                ), '') AS area_text
        ) search
        WHERE {self._text_match_condition()}
            AND (%s::integer IS NULL OR cp.year >= %s::integer)
            AND (%s::integer IS NULL OR cp.year <= %s::integer)
            AND (
                %s::integer IS NULL
                OR EXISTS (
                    SELECT 1
                    FROM conference_paper_researcher cpr_filter
                    WHERE cpr_filter.conference_paper_id = cp.id
                        AND cpr_filter.researcher_id = %s
                )
            )
            AND {self._area_filter_condition()}
        """


    def _advising_query(self) -> str:
        return f"""
        SELECT
            'advising' AS result_type,
            a.id AS id,
            a.title AS title,
            a.year AS year,
            a.researcher_id AS researcher_id,
            jsonb_build_object(
                'id', r.id,
                'full_name', r.full_name
            ) AS primary_researcher,
            jsonb_build_array(jsonb_build_object('id', r.id, 'full_name', r.full_name)) AS authors,
            COALESCE((
                SELECT jsonb_agg(DISTINCT jsonb_build_object(
                    'major_area', ra.major_area,
                    'area', ra.area,
                    'sub_area', ra.sub_area,
                    'specialty', ra.specialty
                ))
                FROM research_area ra
                WHERE ra.researcher_id = a.researcher_id
            ), '[]'::jsonb) AS areas,
            jsonb_build_object(
                'level', a.level,
                'advisee_name', a.advisee_name,
                'advising_type', a.advising_type,
                'institution', a.institution,
                'course', a.course,
                'country', a.country
            ) AS metadata,
            {self._score_expression()}
        FROM advising a
        JOIN researcher r ON r.id = a.researcher_id
        CROSS JOIN LATERAL (
            SELECT
                concat_ws(
                    ' ',
                    a.title,
                    a.level,
                    a.advisee_name,
                    a.advising_type,
                    a.institution,
                    a.course,
                    a.country,
                    r.full_name,
                    r.citation_name,
                    (
                        SELECT string_agg(
                            concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                            ' '
                        )
                        FROM research_area ra
                        WHERE ra.researcher_id = a.researcher_id
                    )
                ) AS text,
                COALESCE((
                    SELECT string_agg(
                        concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                        ' '
                    )
                    FROM research_area ra
                    WHERE ra.researcher_id = a.researcher_id
                ), '') AS area_text
        ) search
        WHERE {self._text_match_condition()}
            AND (%s::integer IS NULL OR a.year >= %s::integer)
            AND (%s::integer IS NULL OR a.year <= %s::integer)
            AND (%s::integer IS NULL OR a.researcher_id = %s::integer)
            AND {self._area_filter_condition()}
        """


    def _researcher_query(self) -> str:
        return f"""
        SELECT
            'researcher' AS result_type,
            r.id AS id,
            r.full_name AS title,
            NULL::INTEGER AS year,
            r.id AS researcher_id,
            jsonb_build_object(
                'id', r.id,
                'full_name', r.full_name
            ) AS primary_researcher,
            '[]'::jsonb AS authors,
            COALESCE((
                SELECT jsonb_agg(DISTINCT jsonb_build_object(
                    'major_area', ra.major_area,
                    'area', ra.area,
                    'sub_area', ra.sub_area,
                    'specialty', ra.specialty
                ))
                FROM research_area ra
                WHERE ra.researcher_id = r.id
            ), '[]'::jsonb) AS areas,
            jsonb_build_object(
                'lattes_id', r.lattes_id,
                'citation_name', r.citation_name,
                'orcid', r.orcid
            ) AS metadata,
            {self._score_expression()}
        FROM researcher r
        CROSS JOIN LATERAL (
            SELECT
                concat_ws(
                    ' ',
                    r.full_name,
                    r.citation_name,
                    r.lattes_id,
                    r.orcid,
                    r.nationality,
                    (
                        SELECT string_agg(
                            concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                            ' '
                        )
                        FROM research_area ra
                        WHERE ra.researcher_id = r.id
                    )
                ) AS text,
                COALESCE((
                    SELECT string_agg(
                        concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty),
                        ' '
                    )
                    FROM research_area ra
                    WHERE ra.researcher_id = r.id
                ), '') AS area_text
        ) search
        WHERE {self._text_match_condition()}
            AND (%s::integer IS NULL OR r.id = %s::integer)
            AND {self._area_filter_condition()}
        """


    def _research_area_query(self) -> str:
        return f"""
        SELECT
            'research_area' AS result_type,
            ra.id AS id,
            concat_ws(
                ' / ',
                ra.major_area,
                ra.area,
                ra.sub_area,
                ra.specialty
            ) AS title,
            NULL::INTEGER AS year,
            ra.researcher_id AS researcher_id,
            jsonb_build_object(
                'id', r.id,
                'full_name', r.full_name
            ) AS primary_researcher,
            '[]'::jsonb AS authors,
            jsonb_build_array(jsonb_build_object(
                'major_area', ra.major_area,
                'area', ra.area,
                'sub_area', ra.sub_area,
                'specialty', ra.specialty
            )) AS areas,
            jsonb_build_object(
                'major_area', ra.major_area,
                'area', ra.area,
                'sub_area', ra.sub_area,
                'specialty', ra.specialty
            ) AS metadata,
            {self._score_expression()}
        FROM research_area ra
        JOIN researcher r ON r.id = ra.researcher_id
        CROSS JOIN LATERAL (
            SELECT
                concat_ws(
                    ' ',
                    ra.major_area,
                    ra.area,
                    ra.sub_area,
                    ra.specialty,
                    r.full_name,
                    r.citation_name
                ) AS text,
                concat_ws(' ', ra.major_area, ra.area, ra.sub_area, ra.specialty) AS area_text
        ) search
        WHERE {self._text_match_condition()}
            AND (%s::integer IS NULL OR ra.researcher_id = %s::integer)
            AND {self._area_filter_condition()}
        """
