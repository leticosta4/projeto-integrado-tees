-- search-indexes
-- depends: 20260628_01_publication-researcher-links

CREATE INDEX papers_title_fts_idx
ON papers USING gin (to_tsvector('portuguese', coalesce(title, '')));

CREATE INDEX conference_paper_title_fts_idx
ON conference_paper USING gin (to_tsvector('portuguese', coalesce(title, '')));

CREATE INDEX advising_title_fts_idx
ON advising USING gin (to_tsvector('portuguese', coalesce(title, '')));

CREATE INDEX researcher_text_fts_idx
ON researcher USING gin (
    to_tsvector(
        'portuguese',
        coalesce(full_name, '') || ' ' ||
        coalesce(citation_name, '') || ' ' ||
        coalesce(lattes_id, '')
    )
);

CREATE INDEX research_area_text_fts_idx
ON research_area USING gin (
    to_tsvector(
        'portuguese',
        coalesce(major_area, '') || ' ' ||
        coalesce(area, '') || ' ' ||
        coalesce(sub_area, '') || ' ' ||
        coalesce(specialty, '')
    )
);

CREATE INDEX papers_year_idx
ON papers (year);

CREATE INDEX conference_paper_year_idx
ON conference_paper (year);

CREATE INDEX advising_year_idx
ON advising (year);

CREATE INDEX papers_researcher_id_idx
ON papers (researcher_id);

CREATE INDEX conference_paper_researcher_id_idx
ON conference_paper (researcher_id);

CREATE INDEX advising_researcher_id_idx
ON advising (researcher_id);

CREATE INDEX research_area_researcher_id_idx
ON research_area (researcher_id);

CREATE INDEX paper_researcher_paper_id_idx
ON paper_researcher (paper_id);

CREATE INDEX conference_paper_researcher_paper_id_idx
ON conference_paper_researcher (conference_paper_id);

CREATE INDEX papers_title_embeddings_hnsw_idx
ON papers USING hnsw (title_embeddings halfvec_cosine_ops)
WHERE title_embeddings IS NOT NULL;
