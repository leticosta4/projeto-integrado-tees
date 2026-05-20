from pydantic import BaseModel

class Advising(BaseModel):
    id: int
    researcher_id: int
    level: str
    title: str
    year: int | None = None
    advisee_name: str | None = None
    advising_type: str | None = None
    institution: str | None = None
    course: str | None = None
    country: str | None = None
    had_scholarship: bool | None = None
    funding_agency: str | None = None
