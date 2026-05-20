from flask import Flask
from tqdm import tqdm

from etl.extractor import Extractor
from etl.models import ResearcherData, XMLData
from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.paper import PaperService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService

def _store_researcher(
    researcher_service: ResearcherService,
    researcher: ResearcherData,
) -> int:
    return researcher_service.add_researcher(
        researcher.full_name,
        researcher.lattes_id,
        researcher.citation_name,
        researcher.orcid,
        researcher.nationality,
        researcher.birth_country,
        researcher.birth_state,
        researcher.update_date,
    )

def _store_papers(
    paper_service: PaperService,
    researcher_id: int,
    researcher: ResearcherData,
) -> None:
    for paper in researcher.papers:
        paper_service.add_paper(
            paper.title,
            researcher_id,
            paper.year,
            paper.doi,
            paper.language,
            paper.nature,
            paper.country,
            paper.journal,
            paper.issn,
            paper.volume,
            paper.issue,
            paper.first_page,
            paper.last_page,
        )

def _store_academic_formations(
    academic_formation_service: AcademicFormationService,
    researcher_id: int,
    researcher: ResearcherData,
) -> None:
    for formation in researcher.academic_formations:
        academic_formation_service.add_academic_formation(
            researcher_id,
            formation.level,
            formation.institution,
            formation.course,
            formation.status,
            formation.start_year,
            formation.end_year,
            formation.thesis_title,
            formation.advisor,
            formation.funding_agency,
            formation.had_scholarship,
        )

def _store_research_areas(
    research_area_service: ResearchAreaService,
    researcher_id: int,
    researcher: ResearcherData,
) -> None:
    for area in researcher.research_areas:
        research_area_service.add_research_area(
            researcher_id,
            area.major_area,
            area.area,
            area.sub_area,
            area.specialty,
        )

def _store_conference_papers(
    conference_paper_service: ConferencePaperService,
    researcher_id: int,
    researcher: ResearcherData,
) -> None:
    for conference_paper in researcher.conference_papers:
        conference_paper_service.add_conference_paper(
            researcher_id,
            conference_paper.title,
            conference_paper.year,
            conference_paper.nature,
            conference_paper.country,
            conference_paper.language,
            conference_paper.doi,
            conference_paper.event_name,
            conference_paper.event_city,
            conference_paper.event_year,
            conference_paper.event_classification,
            conference_paper.proceedings_title,
            conference_paper.isbn,
            conference_paper.first_page,
            conference_paper.last_page,
        )

def _store_advisings(
    advising_service: AdvisingService,
    researcher_id: int,
    researcher: ResearcherData,
) -> None:
    for advising in researcher.advisings:
        advising_service.add_advising(
            researcher_id,
            advising.level,
            advising.title,
            advising.year,
            advising.advisee_name,
            advising.advising_type,
            advising.institution,
            advising.course,
            advising.country,
            advising.had_scholarship,
            advising.funding_agency,
        )

def test_storage(app: Flask):
    data: list[XMLData] = Extractor().extract()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    paper_service: PaperService = app.config['PAPER_SERVICE']
    academic_formation_service: AcademicFormationService = app.config[
        'ACADEMIC_FORMATION_SERVICE'
    ]
    research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
    conference_paper_service: ConferencePaperService = app.config[
        'CONFERENCE_PAPER_SERVICE'
    ]
    advising_service: AdvisingService = app.config['ADVISING_SERVICE']

    assert researcher_service.get_researcher_count() == 0
    assert paper_service.get_paper_count() == 0
    assert academic_formation_service.get_academic_formation_count() == 0
    assert research_area_service.get_research_area_count() == 0
    assert conference_paper_service.get_conference_paper_count() == 0
    assert advising_service.get_advising_count() == 0

    print('[INFO] Storing...')
    for xml in tqdm(data):
        researcher = xml.researcher_data
        researcher_id = _store_researcher(researcher_service, researcher)
        _store_papers(paper_service, researcher_id, researcher)
        _store_academic_formations(
            academic_formation_service,
            researcher_id,
            researcher,
        )
        _store_research_areas(research_area_service, researcher_id, researcher)
        _store_conference_papers(
            conference_paper_service,
            researcher_id,
            researcher,
        )
        _store_advisings(advising_service, researcher_id, researcher)

    assert researcher_service.get_researcher_count() == 8
    assert paper_service.get_paper_count() == 494
    assert academic_formation_service.get_academic_formation_count() == 38
    assert research_area_service.get_research_area_count() == 36
    assert conference_paper_service.get_conference_paper_count() == 325
    assert advising_service.get_advising_count() == 406
