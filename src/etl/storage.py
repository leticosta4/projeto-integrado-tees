from flask import Flask
from service.academic_formation import AcademicFormationService
from service.advising import AdvisingService
from service.conference_paper import ConferencePaperService
from service.research_area import ResearchAreaService
from service.researcher import ResearcherService
from service.paper import PaperService
from tqdm import tqdm

from etl.models import ResearcherData, XMLData

class Storage:
    def __init__(
        self,
        app: Flask
    ) -> None:
        self.academic_formation_service: AcademicFormationService = app.config['ACADEMIC_FORMATION_SERVICE']
        self.advising_service: AdvisingService = app.config['ADVISING_SERVICE']
        self.conference_paper_service: ConferencePaperService = app.config['CONFERENCE_PAPER_SERVICE']
        self.research_area_service: ResearchAreaService = app.config['RESEARCH_AREA_SERVICE']
        self.researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
        self.paper_service: PaperService = app.config['PAPER_SERVICE']

    def _store_researcher(
        self,
        researcher: ResearcherData,
    ) -> int:
        return self.researcher_service.add_researcher(
            researcher.full_name,
            researcher.lattes_id,
            researcher.citation_name,
            researcher.orcid,
            researcher.nationality,
            researcher.birth_country,
            researcher.birth_state,
            researcher.update_date,
        )

    def _store_papers(
        self,
        researcher_id: int,
        researcher: ResearcherData,
    ) -> None:
        for paper in researcher.papers:
            self.paper_service.add_paper(
                paper.title,
                researcher_id,
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

    def _store_academic_formations(
        self,
        researcher_id: int,
        researcher: ResearcherData,
    ) -> None:
        for formation in researcher.academic_formations:
            self.academic_formation_service.add_academic_formation(
                researcher_id,
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

    def _store_research_areas(
        self,
        researcher_id: int,
        researcher: ResearcherData,
    ) -> None:
        for area in researcher.research_areas:
            self.research_area_service.add_research_area(
                researcher_id,
                area.major_area,
                area.area,
                area.sub_area,
                area.specialty,
            )

    def _store_conference_papers(
        self,
        researcher_id: int,
        researcher: ResearcherData,
    ) -> None:
        for conference_paper in researcher.conference_papers:
            self.conference_paper_service.add_conference_paper(
                researcher_id,
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

    def _store_advisings(
        self,
        researcher_id: int,
        researcher: ResearcherData,
    ) -> None:
        for advising in researcher.advisings:
            self.advising_service.add_advising(
                researcher_id,
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

    def store(self, xml_data: list[XMLData]):
        print('[INFO] Storing...')
        for xml in tqdm(xml_data):
            researcher = xml.researcher_data
            researcher_id = self._store_researcher(researcher)
            self._store_papers(researcher_id, researcher)
            self._store_academic_formations(
                researcher_id,
                researcher,
            )
            self._store_research_areas(researcher_id, researcher)
            self._store_conference_papers(
                researcher_id,
                researcher,
            )
            self._store_advisings(researcher_id, researcher)
