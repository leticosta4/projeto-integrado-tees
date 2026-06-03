from etl.models import (
    Advising,
    Paper,
    ResearchArea,
    ResearcherData,
    XMLData,
)
from etl.transformer import Transformer


def make_xml_data() -> XMLData:
    return XMLData(
        filename="sample.xml",
        filehash="hash",
        researcher_data=ResearcherData(
            full_name="  Maria   Silva  ",
            lattes_id=" 123 ",
            citation_name="  SILVA,   M. ",
            orcid="https://orcid.org/0000-0000-0000-0000",
            nationality=" Brasileira ",
            birth_country=" Brasil ",
            birth_state=" ba ",
            update_date="23032026",
            papers=[
                Paper(
                    title="  A   Study ",
                    year=2024,
                    doi="https://doi.org/10.1000/ABC",
                    language=" Inglês ",
                    nature=" completo ",
                    country=" Brasil ",
                    journal=" Journal ",
                    issn="1234-5678",
                    first_page="p. 10",
                    last_page=" 20 ",
                ),
                Paper(
                    title="A Study",
                    year=2024,
                    doi="10.1000/abc",
                ),
            ],
            academic_formations=[],
            research_areas=[
                ResearchArea(
                    major_area="CIENCIAS_DA_SAUDE",
                    area=" Medicina ",
                    sub_area=" Neurociências ",
                ),
                ResearchArea(
                    major_area="CIENCIAS DA SAUDE",
                    area="Medicina",
                    sub_area="Neurociências",
                ),
            ],
            conference_papers=[],
            advisings=[
                Advising(
                    level="MESTRADO",
                    title="  Minha   orientação ",
                    year=2022,
                    advisee_name=" Ana  Souza ",
                    advising_type="CO_ORIENTADOR",
                ),
                Advising(
                    level="MESTRADO",
                    title="Minha orientação",
                    year=2022,
                    advisee_name="Ana Souza",
                ),
            ],
        ),
    )


def test_transformer_normalizes_researcher_data():
    transformed = Transformer().transform([make_xml_data()])[0]
    researcher = transformed.researcher_data

    assert researcher.full_name == "Maria Silva"
    assert researcher.lattes_id == "123"
    assert researcher.citation_name == "SILVA, M."
    assert researcher.orcid == "0000-0000-0000-0000"
    assert researcher.birth_country == "Brasil"
    assert researcher.birth_state == "BA"
    assert researcher.update_date == "2026-03-23"


def test_transformer_cleans_and_deduplicates_papers():
    transformed = Transformer().transform([make_xml_data()])[0]
    papers = transformed.researcher_data.papers

    assert len(papers) == 1
    assert papers[0].title == "A Study"
    assert papers[0].doi == "10.1000/abc"
    assert papers[0].nature == "COMPLETO"
    assert papers[0].issn == "12345678"
    assert papers[0].first_page == "10"
    assert papers[0].last_page == "20"


def test_transformer_normalizes_underscores_and_deduplicates_lists():
    transformed = Transformer().transform([make_xml_data()])[0]
    researcher = transformed.researcher_data

    assert len(researcher.research_areas) == 1
    assert researcher.research_areas[0].major_area == "CIENCIAS DA SAUDE"

    assert len(researcher.advisings) == 1
    assert researcher.advisings[0].title == "Minha orientação"
    assert researcher.advisings[0].advisee_name == "Ana Souza"
    assert researcher.advisings[0].advising_type == "CO ORIENTADOR"
