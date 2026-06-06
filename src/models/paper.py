from pydantic import BaseModel, field_validator
import json

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
    title_embeddings: list[float] | None = None

    @field_validator("title_embeddings", mode="before")
    @classmethod
    def parse_embeddings(cls, v):
        if isinstance(v, str):
            try:
                # Remove brackets and split by comma
                cleaned = v.strip("[]")
                if not cleaned:
                    return []
                return [float(x) for x in cleaned.split(",")]
            except (ValueError, TypeError):
                return None
        return v
