from psycopg_pool import ConnectionPool
from settings import Settings
from flask import Flask

from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.paper import PaperService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService

def create_app():
    app = Flask(__name__)

    # App config

    settings: Settings = Settings()
    app.config['SETTINGS'] = settings

    # Postgres
    
    pool: ConnectionPool = ConnectionPool(
        conninfo=settings.DAO_URL(), min_size=1, max_size=10, open=True
    )
    app.config['POOL'] = pool

    # Services

    app.config['RESEARCHER_SERVICE'] = ResearcherService(pool)
    app.config['PAPER_SERVICE'] = PaperService(pool)
    app.config['ACADEMIC_FORMATION_SERVICE'] = AcademicFormationService(pool)
    app.config['RESEARCH_AREA_SERVICE'] = ResearchAreaService(pool)
    app.config['CONFERENCE_PAPER_SERVICE'] = ConferencePaperService(pool)
    app.config['ADVISING_SERVICE'] = AdvisingService(pool)

    # Blueprints
    #
    # TODO:
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
