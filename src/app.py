from psycopg_pool import ConnectionPool
from settings import Settings
from flask import Flask

from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.paper import PaperService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService
from routes.academic_formation import academic_formation_bp
from routes.advising import advising_bp
from routes.conference_paper import conference_paper_bp
from routes.paper import paper_bp
from routes.research_area import research_area_bp
from routes.researcher import researcher_bp
from routes.swagger import api_bp
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def create_app():
    app = Flask(__name__)

    @app.get("/")
    def home():
        return {
            "message": "Hello World",
            "swagger": "/api/docs",
        }

    # App config

    settings: Settings = Settings()
    app.config['SETTINGS'] = settings

    # Postgres
    
    pool: ConnectionPool = ConnectionPool(
        conninfo=settings.DAO_URL(), min_size=1, max_size=10, open=True
    )
    app.config['POOL'] = pool

    # Services

    embeddings_model = None

    if settings.ENABLE_EMBEDDINGS:
        if (
            settings.GOOGLE_API_KEY is None
            or settings.EMBEDDING_MODEL is None
            or settings.DIMENSIONS is None
        ):
            raise ValueError(
                "GOOGLE_API_KEY, EMBEDDING_MODEL and DIMENSIONS are required "
                "when ENABLE_EMBEDDINGS is true"
            )

        embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.GOOGLE_API_KEY,
            output_dimensionality=settings.DIMENSIONS,
        )

    app.config['RESEARCHER_SERVICE'] = ResearcherService(pool)
    app.config['PAPER_SERVICE'] = PaperService(pool, embeddings_model)
    app.config['ACADEMIC_FORMATION_SERVICE'] = AcademicFormationService(pool)
    app.config['RESEARCH_AREA_SERVICE'] = ResearchAreaService(pool)
    app.config['CONFERENCE_PAPER_SERVICE'] = ConferencePaperService(pool)
    app.config['ADVISING_SERVICE'] = AdvisingService(pool)

    # Blueprints

    app.register_blueprint(api_bp)
    app.register_blueprint(researcher_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(academic_formation_bp)
    app.register_blueprint(research_area_bp)
    app.register_blueprint(conference_paper_bp)
    app.register_blueprint(advising_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
