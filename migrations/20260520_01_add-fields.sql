-- 
-- depends: 20260517_01_baseline

ALTER TABLE researcher ADD COLUMN lattes_id TEXT NOT NULL;
ALTER TABLE researcher ADD COLUMN citation_name TEXT;
ALTER TABLE researcher ADD COLUMN orcid TEXT;
ALTER TABLE researcher ADD COLUMN nationality TEXT;
ALTER TABLE researcher ADD COLUMN birth_country TEXT;
ALTER TABLE researcher ADD COLUMN birth_state TEXT;
ALTER TABLE researcher ADD COLUMN update_date TEXT;

ALTER TABLE papers ADD COLUMN year INTEGER;
ALTER TABLE papers ADD COLUMN doi TEXT;
ALTER TABLE papers ADD COLUMN language TEXT;
ALTER TABLE papers ADD COLUMN nature TEXT;
ALTER TABLE papers ADD COLUMN country TEXT;
ALTER TABLE papers ADD COLUMN journal TEXT;
ALTER TABLE papers ADD COLUMN issn TEXT;
ALTER TABLE papers ADD COLUMN volume TEXT;
ALTER TABLE papers ADD COLUMN issue TEXT;
ALTER TABLE papers ADD COLUMN first_page TEXT;
ALTER TABLE papers ADD COLUMN last_page TEXT;
