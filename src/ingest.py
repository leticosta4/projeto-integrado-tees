from flask import Flask
from app import create_app
from pathlib import Path
from service.researcher import ResearcherService
from service.paper import PaperService

from etl.file_lister import FileLister
from etl.extractor import Extractor
from etl.loader import Loader
from etl.models import XMLData, ResearcherData, XMLLoaded, Paper

from tqdm import tqdm

def main():
    extractor: Extractor = Extractor()
    data: list[XMLData] = extractor.extract()

    app: Flask = create_app()
    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    paper_service: PaperService = app.config['PAPER_SERVICE']

    print('[INFO] Storing...')
    for xml in tqdm(data):
        researcher: ResearcherData = xml.researcher_data
        id = researcher_service.add_researcher(
            researcher.full_name,
            researcher.lattes_id,
            researcher.citation_name,
            researcher.orcid,
            researcher.nationality,
            researcher.birth_country,
            researcher.birth_state,
            researcher.update_date,
        )
        for paper in researcher.papers:
            paper_service.add_paper(
                paper.title,
                id,
                paper.year,
                paper.doi,
                paper.language,
                paper.nature,
                paper.country,
                paper.journal,
                paper.issn,
                paper.volume,
                paper.issue,
                paper.first_page,
                paper.last_page,
            )

if __name__ == "__main__":
    main()
