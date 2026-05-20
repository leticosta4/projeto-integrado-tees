from pydantic import BaseModel

class Researcher(BaseModel):
    id: int
    full_name: str
