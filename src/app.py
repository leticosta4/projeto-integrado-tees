from psycopg_pool import ConnectionPool
from settings import Settings
from flask import Flask, g

from domain.paper.paper_service import PaperService
from domain.researcher.researcher_service import ResearcherService

def create_app():
    app = Flask(__name__)

    # App config

    settings: Settings = Settings()
    app.config['SETTINGS'] = settings

    # Postgres
    
    pool: ConnectionPool = ConnectionPool(
        conninfo=settings.DAO_URL(), min_size=1, max_size=10, open=False
    )
    pool.open()
    app.config['POOL'] = pool

    # Services

    app.config['RESEARCHER_SERVICE'] = ResearcherService(pool)
    app.config['PAPER_SERVICE'] = PaperService(pool)

    @app.teardown_appcontext
    def shutdown(exception):
        pool.close()

    # Blueprints
    #
    # TODO:
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
