from pydantic import BaseModel

class ConferencePaper(BaseModel):
    id: int
    researcher_id: int
    title: str
    year: int | None = None
    nature: str | None = None
    country: str | None = None
    language: str | None = None
    doi: str | None = None
    event_name: str | None = None
    event_city: str | None = None
    event_year: int | None = None
    event_classification: str | None = None
    proceedings_title: str | None = None
    isbn: str | None = None
    first_page: str | None = None
    last_page: str | None = None
