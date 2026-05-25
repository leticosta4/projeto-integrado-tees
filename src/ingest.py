from flask import Flask
from app import create_app
from tqdm import tqdm

from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService
from service.paper import PaperService

from etl.extractor import Extractor
from etl.models import XMLData, ResearcherData
from etl.storage import Storage


def main():
    data: list[XMLData] = Extractor().extract()

    app: Flask = create_app()
    storage: Storage = Storage(app)
    storage.store(data)


if __name__ == "__main__":
    main()
