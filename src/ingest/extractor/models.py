from pydantic import BaseModel

class Paper(BaseModel):
    title: str

class ResearcherData(BaseModel):
    full_name: str
    papers: list[Paper]

class XMLData(BaseModel):
    researcher_data: ResearcherData
    filename: str
    filehash: str
