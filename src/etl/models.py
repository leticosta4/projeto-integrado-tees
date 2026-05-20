from typing import TypedDict
from pydantic import BaseModel
from xml.etree.ElementTree import ElementTree

# Loader model
class XMLLoaded(TypedDict):
    filename: str
    filehash: str
    data: ElementTree


# Extractor models
class Paper(BaseModel):
    title: str
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

class ResearcherData(BaseModel):
    full_name: str
    lattes_id: str
    citation_name: str | None = None
    orcid: str | None = None
    nationality: str | None = None
    birth_country: str | None = None
    birth_state: str | None = None
    update_date: str | None = None
    papers: list[Paper]

class XMLData(BaseModel):
    researcher_data: ResearcherData
    filename: str
    filehash: str
