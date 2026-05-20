from flask import Flask
from app import create_app
import pytest

from service.researcher import ResearcherService
from service.paper import PaperService

@pytest.fixture()
def app():
    app: Flask = create_app()
    app.config.update({
        'TESTING': True
    })

    # Delete data

    paper_service: PaperService = app.config['PAPER_SERVICE']
    paper_service.remove_all_papers()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    researcher_service.remove_all_researchers()

    with app.app_context():
        yield app

    # Delete data
    paper_service: PaperService = app.config['PAPER_SERVICE']
    paper_service.remove_all_papers()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    researcher_service.remove_all_researchers()

@pytest.fixture()
def client(app: Flask):
    return app.test_client()
