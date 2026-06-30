-- publication-researcher-links
-- depends: 20260525_02_BqMCl-vector-column

ALTER TABLE papers ADD COLUMN normalized_title TEXT;
ALTER TABLE conference_paper ADD COLUMN normalized_title TEXT;

UPDATE papers
SET normalized_title = lower(regexp_replace(btrim(title), '\s+', ' ', 'g'))
WHERE normalized_title IS NULL;

UPDATE conference_paper
SET normalized_title = lower(regexp_replace(btrim(title), '\s+', ' ', 'g'))
WHERE normalized_title IS NULL;

CREATE TABLE paper_researcher (
    paper_id INTEGER NOT NULL,
    researcher_id INTEGER NOT NULL,
    author_order INTEGER,
    role TEXT DEFAULT 'author',
    source TEXT DEFAULT 'lattes_xml',
    matched_by TEXT DEFAULT 'legacy_researcher_id',
    PRIMARY KEY (paper_id, researcher_id),
    FOREIGN KEY(paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id) ON DELETE CASCADE
);

CREATE TABLE conference_paper_researcher (
    conference_paper_id INTEGER NOT NULL,
    researcher_id INTEGER NOT NULL,
    author_order INTEGER,
    role TEXT DEFAULT 'author',
    source TEXT DEFAULT 'lattes_xml',
    matched_by TEXT DEFAULT 'legacy_researcher_id',
    PRIMARY KEY (conference_paper_id, researcher_id),
    FOREIGN KEY(conference_paper_id) REFERENCES conference_paper(id) ON DELETE CASCADE,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id) ON DELETE CASCADE
);

WITH ranked_papers AS (
    SELECT
        id,
        researcher_id,
        min(id) OVER (
            PARTITION BY
                CASE
                    WHEN nullif(btrim(doi), '') IS NOT NULL
                        THEN 'doi:' || lower(btrim(doi))
                    ELSE
                        'title:' || coalesce(normalized_title, '') ||
                        '|year:' || coalesce(year::TEXT, '') ||
                        '|journal:' || coalesce(lower(btrim(journal)), '') ||
                        '|issn:' || coalesce(issn, '')
                END
        ) AS canonical_id,
        CASE
            WHEN nullif(btrim(doi), '') IS NOT NULL THEN 'doi'
            ELSE 'normalized_title_year_journal'
        END AS matched_by
    FROM papers
)
INSERT INTO paper_researcher (
    paper_id,
    researcher_id,
    author_order,
    role,
    source,
    matched_by
)
SELECT
    canonical_id,
    researcher_id,
    NULL,
    'author',
    'legacy_import',
    matched_by
FROM ranked_papers
ON CONFLICT DO NOTHING;

WITH ranked_papers AS (
    SELECT
        id,
        min(id) OVER (
            PARTITION BY
                CASE
                    WHEN nullif(btrim(doi), '') IS NOT NULL
                        THEN 'doi:' || lower(btrim(doi))
                    ELSE
                        'title:' || coalesce(normalized_title, '') ||
                        '|year:' || coalesce(year::TEXT, '') ||
                        '|journal:' || coalesce(lower(btrim(journal)), '') ||
                        '|issn:' || coalesce(issn, '')
                END
        ) AS canonical_id
    FROM papers
)
DELETE FROM papers
USING ranked_papers
WHERE papers.id = ranked_papers.id
    AND papers.id <> ranked_papers.canonical_id;

WITH ranked_conference_papers AS (
    SELECT
        id,
        researcher_id,
        min(id) OVER (
            PARTITION BY
                CASE
                    WHEN nullif(btrim(doi), '') IS NOT NULL
                        THEN 'doi:' || lower(btrim(doi))
                    ELSE
                        'title:' || coalesce(normalized_title, '') ||
                        '|year:' || coalesce(year::TEXT, '') ||
                        '|event:' || coalesce(lower(btrim(event_name)), '') ||
                        '|proceedings:' || coalesce(lower(btrim(proceedings_title)), '') ||
                        '|isbn:' || coalesce(isbn, '')
                END
        ) AS canonical_id,
        CASE
            WHEN nullif(btrim(doi), '') IS NOT NULL THEN 'doi'
            ELSE 'normalized_title_year_event'
        END AS matched_by
    FROM conference_paper
)
INSERT INTO conference_paper_researcher (
    conference_paper_id,
    researcher_id,
    author_order,
    role,
    source,
    matched_by
)
SELECT
    canonical_id,
    researcher_id,
    NULL,
    'author',
    'legacy_import',
    matched_by
FROM ranked_conference_papers
ON CONFLICT DO NOTHING;

WITH ranked_conference_papers AS (
    SELECT
        id,
        min(id) OVER (
            PARTITION BY
                CASE
                    WHEN nullif(btrim(doi), '') IS NOT NULL
                        THEN 'doi:' || lower(btrim(doi))
                    ELSE
                        'title:' || coalesce(normalized_title, '') ||
                        '|year:' || coalesce(year::TEXT, '') ||
                        '|event:' || coalesce(lower(btrim(event_name)), '') ||
                        '|proceedings:' || coalesce(lower(btrim(proceedings_title)), '') ||
                        '|isbn:' || coalesce(isbn, '')
                END
        ) AS canonical_id
    FROM conference_paper
)
DELETE FROM conference_paper
USING ranked_conference_papers
WHERE conference_paper.id = ranked_conference_papers.id
    AND conference_paper.id <> ranked_conference_papers.canonical_id;

CREATE UNIQUE INDEX papers_unique_doi
ON papers (lower(btrim(doi)))
WHERE nullif(btrim(doi), '') IS NOT NULL;

CREATE UNIQUE INDEX papers_unique_normalized_title_year_journal
ON papers (
    normalized_title,
    (coalesce(year, 0)),
    (coalesce(lower(btrim(journal)), '')),
    (coalesce(issn, ''))
)
WHERE nullif(btrim(doi), '') IS NULL;

CREATE UNIQUE INDEX conference_paper_unique_doi
ON conference_paper (lower(btrim(doi)))
WHERE nullif(btrim(doi), '') IS NOT NULL;

CREATE UNIQUE INDEX conference_paper_unique_normalized_title_year_event
ON conference_paper (
    normalized_title,
    (coalesce(year, 0)),
    (coalesce(lower(btrim(event_name)), '')),
    (coalesce(lower(btrim(proceedings_title)), '')),
    (coalesce(isbn, ''))
)
WHERE nullif(btrim(doi), '') IS NULL;

CREATE INDEX paper_researcher_researcher_id_idx
ON paper_researcher (researcher_id);

CREATE INDEX conference_paper_researcher_researcher_id_idx
ON conference_paper_researcher (researcher_id);
