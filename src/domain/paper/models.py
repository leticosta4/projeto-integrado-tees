from pydantic import BaseModel

class Paper(BaseModel):
    id: int
    title: str
    researcher_id: int
