from flask import Flask
from app import create_app
from settings import Settings
import pytest
from domain.researcher.researcher_service import ResearcherService
from domain.paper.paper_service import PaperService
from psycopg_pool import ConnectionPool

@pytest.fixture()
async def app():
    app = create_app()
    app.config.update({
        'TESTING': True
    })
    pool: ConnectionPool = app.config['POOL']
    pool.open()
    with app.test_app():
        yield app
    pool.close()

@pytest.fixture()
def client(app: Flask):
    return app.test_client()
