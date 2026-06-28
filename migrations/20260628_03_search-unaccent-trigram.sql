-- search-unaccent-trigram
-- depends: 20260628_02_search-indexes

CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE OR REPLACE FUNCTION immutable_unaccent(value text)
RETURNS text
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT public.unaccent('public.unaccent'::regdictionary, value)
$$;

CREATE INDEX papers_search_text_trgm_idx
ON papers USING gin (
    immutable_unaccent(lower(
        coalesce(title, '') || ' ' ||
        coalesce(doi, '') || ' ' ||
        coalesce(journal, '') || ' ' ||
        coalesce(issn, '') || ' ' ||
        coalesce(nature, '') || ' ' ||
        coalesce(language, '') || ' ' ||
        coalesce(country, '')
    )) gin_trgm_ops
);

CREATE INDEX conference_paper_search_text_trgm_idx
ON conference_paper USING gin (
    immutable_unaccent(lower(
        coalesce(title, '') || ' ' ||
        coalesce(doi, '') || ' ' ||
        coalesce(event_name, '') || ' ' ||
        coalesce(event_city, '') || ' ' ||
        coalesce(event_classification, '') || ' ' ||
        coalesce(proceedings_title, '') || ' ' ||
        coalesce(isbn, '') || ' ' ||
        coalesce(nature, '') || ' ' ||
        coalesce(language, '') || ' ' ||
        coalesce(country, '')
    )) gin_trgm_ops
);

CREATE INDEX advising_search_text_trgm_idx
ON advising USING gin (
    immutable_unaccent(lower(
        coalesce(title, '') || ' ' ||
        coalesce(level, '') || ' ' ||
        coalesce(advisee_name, '') || ' ' ||
        coalesce(advising_type, '') || ' ' ||
        coalesce(institution, '') || ' ' ||
        coalesce(course, '') || ' ' ||
        coalesce(country, '')
    )) gin_trgm_ops
);

CREATE INDEX researcher_search_text_trgm_idx
ON researcher USING gin (
    immutable_unaccent(lower(
        coalesce(full_name, '') || ' ' ||
        coalesce(citation_name, '') || ' ' ||
        coalesce(lattes_id, '') || ' ' ||
        coalesce(orcid, '') || ' ' ||
        coalesce(nationality, '')
    )) gin_trgm_ops
);

CREATE INDEX research_area_search_text_trgm_idx
ON research_area USING gin (
    immutable_unaccent(lower(
        coalesce(major_area, '') || ' ' ||
        coalesce(area, '') || ' ' ||
        coalesce(sub_area, '') || ' ' ||
        coalesce(specialty, '')
    )) gin_trgm_ops
);
