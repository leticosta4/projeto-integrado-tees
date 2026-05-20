from pydantic import BaseModel

class Paper(BaseModel):
    id: int
    title: str
    researcher_id: int
    year: int | None = None
    doi: str | None = None
    language: str | None = None
    nature: str | None = None
    country: str | None = None
    journal: str | None = None
    issn: str | None = None
    volume: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None
