from pydantic import BaseModel


class ConferencePaperResearcher(BaseModel):
    conference_paper_id: int
    researcher_id: int
    author_order: int | None = None
    role: str | None = None
    source: str | None = None
    matched_by: str | None = None
