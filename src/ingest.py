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



def main():
    extractor: Extractor = Extractor()
    data: list[XMLData] = extractor.extract()

    app: Flask = create_app()
    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    paper_service: PaperService = app.config['PAPER_SERVICE']
    academic_formation_service: AcademicFormationService = app.config[
        'ACADEMIC_FORMATION_SERVICE'
    ]
    research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
    conference_paper_service: ConferencePaperService = app.config[
        'CONFERENCE_PAPER_SERVICE'
    ]
    advising_service: AdvisingService = app.config['ADVISING_SERVICE']

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

        for formation in researcher.academic_formations:
            academic_formation_service.add_academic_formation(
                id,
                formation.level,
                formation.institution,
                formation.course,
                formation.status,
                formation.start_year,
                formation.end_year,
                formation.thesis_title,
                formation.advisor,
                formation.funding_agency,
                formation.had_scholarship,
            )

        for area in researcher.research_areas:
            research_area_service.add_research_area(
                id,
                area.major_area,
                area.area,
                area.sub_area,
                area.specialty,
            )

        for conference_paper in researcher.conference_papers:
            conference_paper_service.add_conference_paper(
                id,
                conference_paper.title,
                conference_paper.year,
                conference_paper.nature,
                conference_paper.country,
                conference_paper.language,
                conference_paper.doi,
                conference_paper.event_name,
                conference_paper.event_city,
                conference_paper.event_year,
                conference_paper.event_classification,
                conference_paper.proceedings_title,
                conference_paper.isbn,
                conference_paper.first_page,
                conference_paper.last_page,
            )

        for advising in researcher.advisings:
            advising_service.add_advising(
                id,
                advising.level,
                advising.title,
                advising.year,
                advising.advisee_name,
                advising.advising_type,
                advising.institution,
                advising.course,
                advising.country,
                advising.had_scholarship,
                advising.funding_agency,
            )

if __name__ == "__main__":
    main()
