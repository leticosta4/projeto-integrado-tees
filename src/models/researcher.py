from pydantic import BaseModel

class Researcher(BaseModel):
    id: int
    full_name: str
    lattes_id: str
    citation_name: str | None = None
    orcid: str | None = None
    nationality: str | None = None
    birth_country: str | None = None
    birth_state: str | None = None
    update_date: str | None = None
