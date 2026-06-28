from psycopg_pool import ConnectionPool
from settings import Settings
from flask import Flask, request

from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.conference_paper_researcher import ConferencePaperResearcherService
from service.paper import PaperService
from service.paper_researcher import PaperResearcherService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService
from service.search import SearchService
from routes.academic_formation import academic_formation_bp
from routes.advising import advising_bp
from routes.conference_paper import conference_paper_bp
from routes.conference_paper_researcher import conference_paper_researcher_bp
from routes.paper import paper_bp
from routes.paper_researcher import paper_researcher_bp
from routes.research_area import research_area_bp
from routes.researcher import researcher_bp
from routes.search import search_bp
from routes.swagger import api_bp
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def create_app():
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        allowed_origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        }
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return response

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
        embedding_model, api_key, dimensions = settings.EMBEDDINGS_CONFIG()

        embeddings_model = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            api_key=api_key,
            output_dimensionality=dimensions,
        )

    app.config['RESEARCHER_SERVICE'] = ResearcherService(pool)
    app.config['SEARCH_SERVICE'] = SearchService(pool)
    app.config['PAPER_SERVICE'] = PaperService(pool, embeddings_model)
    app.config['PAPER_RESEARCHER_SERVICE'] = PaperResearcherService(pool)
    app.config['ACADEMIC_FORMATION_SERVICE'] = AcademicFormationService(pool)
    app.config['RESEARCH_AREA_SERVICE'] = ResearchAreaService(pool)
    app.config['CONFERENCE_PAPER_SERVICE'] = ConferencePaperService(pool)
    app.config['CONFERENCE_PAPER_RESEARCHER_SERVICE'] = (
        ConferencePaperResearcherService(pool)
    )
    app.config['ADVISING_SERVICE'] = AdvisingService(pool)

    # Blueprints

    app.register_blueprint(api_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(researcher_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(paper_researcher_bp)
    app.register_blueprint(academic_formation_bp)
    app.register_blueprint(research_area_bp)
    app.register_blueprint(conference_paper_bp)
    app.register_blueprint(conference_paper_researcher_bp)
    app.register_blueprint(advising_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
