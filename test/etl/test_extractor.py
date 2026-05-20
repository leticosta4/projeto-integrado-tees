import pytest

from etl.extractor import Extractor
from etl.models import ResearcherData, XMLData

SAMPLE_FILENAME = '1608472474770322.xml'


@pytest.fixture(scope="module")
def extracted_results() -> list[XMLData]:
    return Extractor().extract()


@pytest.fixture(scope="module")
def researchers_data(extracted_results: list[XMLData]) -> list[ResearcherData]:
    return [d.researcher_data for d in extracted_results]


@pytest.fixture(scope="module")
def sample_researcher(extracted_results: list[XMLData]) -> ResearcherData:
    return next(
        d.researcher_data
        for d in extracted_results
        if d.filename == SAMPLE_FILENAME
    )


def test_extract_researcher(
    extracted_results: list[XMLData],
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert extracted_results is not None
    assert isinstance(extracted_results, list)
    assert all(isinstance(x, XMLData) for x in extracted_results)
    assert len(extracted_results) == 8

    full_names: list[str] = [d.full_name for d in researchers_data]
    assert any('Eduardo' in name for name in full_names)

    assert sample_researcher.lattes_id == '1608472474770322'
    assert sample_researcher.update_date == '23032026'
    assert sample_researcher.birth_country == 'Brasil'
    assert sample_researcher.birth_state == 'BA'
    assert sample_researcher.orcid == 'https://orcid.org/0000-0002-7752-8319'
    assert sample_researcher.citation_name is not None


def test_extract_paper(
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert any(
        'experiments' in paper.title
        for researcher in researchers_data
        for paper in researcher.papers
    )

    paper = next(
        paper
        for paper in sample_researcher.papers
        if paper.title == (
            'R/S analysis of pluviometric records: '
            'comparison with numerical experiments'
        )
    )
    assert paper.year == 2001
    assert paper.language == 'Inglês'
    assert paper.nature == 'COMPLETO'
    assert paper.country == 'Brasil'
    assert paper.journal == 'Physica. A'
    assert paper.issn == '03784371'
    assert paper.volume == '295'
    assert paper.first_page == '38'
    assert paper.last_page == '41'


def test_extract_academic_formation(
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert sum(len(r.academic_formations) for r in researchers_data) == 38

    assert len(sample_researcher.academic_formations) == 6
    formation = sample_researcher.academic_formations[0]
    assert formation.level == 'GRADUACAO'
    assert formation.institution == 'Universidade Federal de Minas Gerais'
    assert formation.course == 'Física'
    assert formation.start_year == 1992
    assert formation.end_year == 1995
    assert formation.had_scholarship is True


def test_extract_research_area(
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert sum(len(r.research_areas) for r in researchers_data) == 36

    assert len(sample_researcher.research_areas) == 6
    area = sample_researcher.research_areas[0]
    assert area.major_area == 'CIENCIAS_DA_SAUDE'
    assert area.area == 'Medicina'
    assert area.sub_area == 'Neurociências'


def test_extract_conference_paper(
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert sum(len(r.conference_papers) for r in researchers_data) == 325

    assert len(sample_researcher.conference_papers) == 103
    conference_paper = sample_researcher.conference_papers[0]
    assert conference_paper.year == 1998
    assert conference_paper.nature == 'COMPLETO'
    assert conference_paper.country == 'Espanha'
    assert conference_paper.event_name == 'IV Congreso Nacional de Medio Ambiente'
    assert conference_paper.event_city == 'Madrid'
    assert conference_paper.first_page == '143'
    assert conference_paper.last_page == '158'


def test_extract_advising(
    researchers_data: list[ResearcherData],
    sample_researcher: ResearcherData,
):
    assert sum(len(r.advisings) for r in researchers_data) == 406

    assert len(sample_researcher.advisings) == 78
    advising = sample_researcher.advisings[0]
    assert advising.level == 'MESTRADO'
    assert advising.year == 2003
    assert advising.advisee_name == 'Cristiane da Silva Ferreira'
    assert advising.advising_type == 'CO_ORIENTADOR'
    assert advising.institution == 'Universidade Federal da Bahia'
    assert advising.had_scholarship is True
