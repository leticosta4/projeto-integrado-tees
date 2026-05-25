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

from etl.storage import Storage

def test_storage(app: Flask):
    data: list[XMLData] = Extractor().extract()

    academic_formation_service: AcademicFormationService = app.config['ACADEMIC_FORMATION_SERVICE']
    advising_service: AdvisingService = app.config['ADVISING_SERVICE']
    conference_paper_service: ConferencePaperService = app.config['CONFERENCE_PAPER_SERVICE']
    research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    paper_service: PaperService = app.config['PAPER_SERVICE']

    assert researcher_service.get_researcher_count() == 0
    assert paper_service.get_paper_count() == 0
    assert academic_formation_service.get_academic_formation_count() == 0
    assert research_area_service.get_research_area_count() == 0
    assert conference_paper_service.get_conference_paper_count() == 0
    assert advising_service.get_advising_count() == 0

    storage: Storage = Storage(app)
    storage.store(data)

    assert researcher_service.get_researcher_count() == 8
    assert paper_service.get_paper_count() == 494
    assert academic_formation_service.get_academic_formation_count() == 38
    assert research_area_service.get_research_area_count() == 36
    assert conference_paper_service.get_conference_paper_count() == 325
    assert advising_service.get_advising_count() == 406

    # Dedup

    """
    storage.store(data)

    assert researcher_service.get_researcher_count() == 8
    assert paper_service.get_paper_count() == 494
    assert academic_formation_service.get_academic_formation_count() == 38
    assert research_area_service.get_research_area_count() == 36
    assert conference_paper_service.get_conference_paper_count() == 325
    assert advising_service.get_advising_count() == 406
    """
