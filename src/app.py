from flask import Flask
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from psycopg_pool import ConnectionPool
from settings import Settings

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
    app.config["SETTINGS"] = settings

    # Postgres

    pool: ConnectionPool = ConnectionPool(
        conninfo=settings.DAO_URL(), min_size=1, max_size=10, open=True
    )
    app.config["POOL"] = pool

    # Services

    embeddings_model = None
    if settings.ENABLE_EMBEDDINGS:
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.GOOGLE_API_KEY,
            output_dimensionality=settings.DIMENSIONS,
        )

    app.config["RESEARCHER_SERVICE"] = ResearcherService(pool)
    app.config["PAPER_SERVICE"] = PaperService(pool, embeddings_model)
    app.config["ACADEMIC_FORMATION_SERVICE"] = AcademicFormationService(pool)
    app.config["RESEARCH_AREA_SERVICE"] = ResearchAreaService(pool)
    app.config["CONFERENCE_PAPER_SERVICE"] = ConferencePaperService(pool)
    app.config["ADVISING_SERVICE"] = AdvisingService(pool)

    from routes.api import api
    from routes.web import web

    app.register_blueprint(web)
    app.register_blueprint(api)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
