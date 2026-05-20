from pydantic import BaseModel

class ResearchArea(BaseModel):
    id: int
    researcher_id: int
    major_area: str | None = None
    area: str | None = None
    sub_area: str | None = None
    specialty: str | None = None
