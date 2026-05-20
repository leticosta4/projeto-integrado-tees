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

class ResearcherData(BaseModel):
    full_name: str
    papers: list[Paper]

class XMLData(BaseModel):
    researcher_data: ResearcherData
    filename: str
    filehash: str
