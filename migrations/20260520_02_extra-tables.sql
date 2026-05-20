-- 
-- depends: 20260520_01_add-fields

CREATE TABLE academic_formation (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    researcher_id INTEGER NOT NULL,
    level TEXT NOT NULL,
    institution TEXT,
    course TEXT,
    status TEXT,
    start_year INTEGER,
    end_year INTEGER,
    thesis_title TEXT,
    advisor TEXT,
    funding_agency TEXT,
    had_scholarship BOOLEAN,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id)
);

CREATE TABLE research_area (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    researcher_id INTEGER NOT NULL,
    major_area TEXT,
    area TEXT,
    sub_area TEXT,
    specialty TEXT,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id)
);

CREATE TABLE conference_paper (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    researcher_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    nature TEXT,
    country TEXT,
    language TEXT,
    doi TEXT,
    event_name TEXT,
    event_city TEXT,
    event_year INTEGER,
    event_classification TEXT,
    proceedings_title TEXT,
    isbn TEXT,
    first_page TEXT,
    last_page TEXT,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id)
);

CREATE TABLE advising (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    researcher_id INTEGER NOT NULL,
    level TEXT NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    advisee_name TEXT,
    advising_type TEXT,
    institution TEXT,
    course TEXT,
    country TEXT,
    had_scholarship BOOLEAN,
    funding_agency TEXT,
    FOREIGN KEY(researcher_id) REFERENCES researcher(id)
);
