from flask import Flask
from app import create_app
import pytest

from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.researcher import ResearcherService
from service.paper import PaperService
from service.research_area import ResearchAreaService

@pytest.fixture()
def app():
    app: Flask = create_app()
    app.config.update({
        'TESTING': True
    })

    # Delete data

    advising_service: AdvisingService = app.config['ADVISING_SERVICE']
    advising_service.remove_all_advisings()

    conference_paper_service: ConferencePaperService = app.config[
        'CONFERENCE_PAPER_SERVICE'
    ]
    conference_paper_service.remove_all_conference_papers()

    research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
    research_area_service.remove_all_research_areas()

    academic_formation_service: AcademicFormationService = app.config[
        'ACADEMIC_FORMATION_SERVICE'
    ]
    academic_formation_service.remove_all_academic_formations()

    paper_service: PaperService = app.config['PAPER_SERVICE']
    paper_service.remove_all_papers()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    researcher_service.remove_all_researchers()

    with app.app_context():
        yield app

    # Delete data
    advising_service: AdvisingService = app.config['ADVISING_SERVICE']
    advising_service.remove_all_advisings()

    conference_paper_service: ConferencePaperService = app.config[
        'CONFERENCE_PAPER_SERVICE'
    ]
    conference_paper_service.remove_all_conference_papers()

    research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
    research_area_service.remove_all_research_areas()

    academic_formation_service: AcademicFormationService = app.config[
        'ACADEMIC_FORMATION_SERVICE'
    ]
    academic_formation_service.remove_all_academic_formations()

    paper_service: PaperService = app.config['PAPER_SERVICE']
    paper_service.remove_all_papers()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    researcher_service.remove_all_researchers()

@pytest.fixture()
def client(app: Flask):
    return app.test_client()
