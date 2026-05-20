from pydantic import BaseModel

class AcademicFormation(BaseModel):
    id: int
    researcher_id: int
    level: str
    institution: str | None = None
    course: str | None = None
    status: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    thesis_title: str | None = None
    advisor: str | None = None
    funding_agency: str | None = None
    had_scholarship: bool | None = None
