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
    title_embeddings: list[float] | None = None


class AcademicFormation(BaseModel):
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


class ResearchArea(BaseModel):
    major_area: str | None = None
    area: str | None = None
    sub_area: str | None = None
    specialty: str | None = None


class ConferencePaper(BaseModel):
    title: str
    year: int | None = None
    nature: str | None = None
    country: str | None = None
    language: str | None = None
    doi: str | None = None
    event_name: str | None = None
    event_city: str | None = None
    event_year: int | None = None
    event_classification: str | None = None
    proceedings_title: str | None = None
    isbn: str | None = None
    first_page: str | None = None
    last_page: str | None = None


class Advising(BaseModel):
    level: str
    title: str
    year: int | None = None
    advisee_name: str | None = None
    advising_type: str | None = None
    institution: str | None = None
    course: str | None = None
    country: str | None = None
    had_scholarship: bool | None = None
    funding_agency: str | None = None


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
    academic_formations: list[AcademicFormation]
    research_areas: list[ResearchArea]
    conference_papers: list[ConferencePaper]
    advisings: list[Advising]


class XMLData(BaseModel):
    researcher_data: ResearcherData
    filename: str
    filehash: str
