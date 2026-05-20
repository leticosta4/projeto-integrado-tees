from tqdm import tqdm
from xml.etree.ElementTree import Element

from etl.loader import Loader
from etl.models import (
    AcademicFormation,
    Advising,
    ConferencePaper,
    Paper,
    ResearchArea,
    ResearcherData,
    XMLData,
    XMLLoaded,
)

class Extractor:
    def __init__(self):
        self.loader: Loader = Loader()

    def _get_attribute(self, element: Element | None, name: str) -> str | None:
        if element is None:
            return None

        value = element.get(name)
        if value == "":
            return None

        return value

    def _get_int_attribute(self, element: Element | None, name: str) -> int | None:
        value = self._get_attribute(element, name)
        if value is None:
            return None

        try:
            return int(value)
        except ValueError:
            return None

    def _get_bool_attribute(self, element: Element | None, name: str) -> bool | None:
        value = self._get_attribute(element, name)
        if value is None:
            return None

        if value == "SIM":
            return True

        if value in {"NAO", "NÃO"}:
            return False

        return None

    def _find_child_with_prefix(self, element: Element, prefix: str) -> Element | None:
        for child in element:
            if child.tag.startswith(prefix):
                return child

        return None

    def _get_researcher_data(
        self,
        root: Element,
        papers: list[Paper],
        academic_formations: list[AcademicFormation],
        research_areas: list[ResearchArea],
        conference_papers: list[ConferencePaper],
        advisings: list[Advising],
    ) -> ResearcherData:
        dados_gerais: Element[str] | None = root.find('DADOS-GERAIS')

        return ResearcherData(
            full_name=self._get_attribute(dados_gerais, "NOME-COMPLETO") or "",
            lattes_id=self._get_attribute(root, "NUMERO-IDENTIFICADOR") or "",
            citation_name=self._get_attribute(
                dados_gerais, "NOME-EM-CITACOES-BIBLIOGRAFICAS"
            ),
            orcid=self._get_attribute(dados_gerais, "ORCID-ID"),
            nationality=self._get_attribute(dados_gerais, "NACIONALIDADE"),
            birth_country=self._get_attribute(dados_gerais, "PAIS-DE-NASCIMENTO"),
            birth_state=self._get_attribute(dados_gerais, "UF-NASCIMENTO"),
            update_date=self._get_attribute(root, "DATA-ATUALIZACAO"),
            papers=papers,
            academic_formations=academic_formations,
            research_areas=research_areas,
            conference_papers=conference_papers,
            advisings=advisings,
        )

    def _get_papers(self, root: Element) -> list[Paper]:
        paper_elements = root.findall(".//ARTIGO-PUBLICADO")

        papers: list[Paper] = []

        for paper_element in paper_elements:
            basic_data = paper_element.find("DADOS-BASICOS-DO-ARTIGO")
            details = paper_element.find("DETALHAMENTO-DO-ARTIGO")
            title = self._get_attribute(basic_data, "TITULO-DO-ARTIGO")

            if title is not None:
                papers.append(
                    Paper(
                        title=title,
                        year=self._get_int_attribute(basic_data, "ANO-DO-ARTIGO"),
                        doi=self._get_attribute(basic_data, "DOI"),
                        language=self._get_attribute(basic_data, "IDIOMA"),
                        nature=self._get_attribute(basic_data, "NATUREZA"),
                        country=self._get_attribute(
                            basic_data, "PAIS-DE-PUBLICACAO"
                        ),
                        journal=self._get_attribute(
                            details, "TITULO-DO-PERIODICO-OU-REVISTA"
                        ),
                        issn=self._get_attribute(details, "ISSN"),
                        volume=self._get_attribute(details, "VOLUME"),
                        issue=self._get_attribute(details, "FASCICULO"),
                        first_page=self._get_attribute(details, "PAGINA-INICIAL"),
                        last_page=self._get_attribute(details, "PAGINA-FINAL"),
                    )
                )

        return papers

    def _get_academic_formations(self, root: Element) -> list[AcademicFormation]:
        formation_tags = {
            "GRADUACAO",
            "ESPECIALIZACAO",
            "MESTRADO",
            "DOUTORADO",
            "POS-DOUTORADO",
        }
        formation_elements = root.findall(".//FORMACAO-ACADEMICA-TITULACAO/*")

        formations: list[AcademicFormation] = []
        for formation in formation_elements:
            if formation.tag not in formation_tags:
                continue

            formations.append(
                AcademicFormation(
                    level=formation.tag,
                    institution=self._get_attribute(formation, "NOME-INSTITUICAO"),
                    course=self._get_attribute(formation, "NOME-CURSO"),
                    status=self._get_attribute(formation, "STATUS-DO-CURSO"),
                    start_year=self._get_int_attribute(formation, "ANO-DE-INICIO"),
                    end_year=self._get_int_attribute(formation, "ANO-DE-CONCLUSAO"),
                    thesis_title=(
                        self._get_attribute(formation, "TITULO-DA-DISSERTACAO-TESE")
                        or self._get_attribute(
                            formation, "TITULO-DO-TRABALHO-DE-CONCLUSAO-DE-CURSO"
                        )
                        or self._get_attribute(formation, "TITULO-DO-TRABALHO")
                    ),
                    advisor=(
                        self._get_attribute(
                            formation, "NOME-COMPLETO-DO-ORIENTADOR"
                        )
                        or self._get_attribute(formation, "NOME-DO-ORIENTADOR")
                    ),
                    funding_agency=self._get_attribute(formation, "NOME-AGENCIA"),
                    had_scholarship=self._get_bool_attribute(formation, "FLAG-BOLSA"),
                )
            )

        return formations

    def _get_research_areas(self, root: Element) -> list[ResearchArea]:
        area_elements = root.findall(".//AREAS-DE-ATUACAO/AREA-DE-ATUACAO")

        return [
            ResearchArea(
                major_area=self._get_attribute(
                    area, "NOME-GRANDE-AREA-DO-CONHECIMENTO"
                ),
                area=self._get_attribute(area, "NOME-DA-AREA-DO-CONHECIMENTO"),
                sub_area=self._get_attribute(
                    area, "NOME-DA-SUB-AREA-DO-CONHECIMENTO"
                ),
                specialty=self._get_attribute(area, "NOME-DA-ESPECIALIDADE"),
            )
            for area in area_elements
        ]

    def _get_conference_papers(self, root: Element) -> list[ConferencePaper]:
        conference_elements = root.findall(".//TRABALHOS-EM-EVENTOS/TRABALHO-EM-EVENTOS")

        conference_papers: list[ConferencePaper] = []
        for conference in conference_elements:
            basic_data = conference.find("DADOS-BASICOS-DO-TRABALHO")
            details = conference.find("DETALHAMENTO-DO-TRABALHO")
            title = self._get_attribute(basic_data, "TITULO-DO-TRABALHO")

            if title is None:
                continue

            conference_papers.append(
                ConferencePaper(
                    title=title,
                    year=self._get_int_attribute(basic_data, "ANO-DO-TRABALHO"),
                    nature=self._get_attribute(basic_data, "NATUREZA"),
                    country=self._get_attribute(basic_data, "PAIS-DO-EVENTO"),
                    language=self._get_attribute(basic_data, "IDIOMA"),
                    doi=self._get_attribute(basic_data, "DOI"),
                    event_name=self._get_attribute(details, "NOME-DO-EVENTO"),
                    event_city=self._get_attribute(details, "CIDADE-DO-EVENTO"),
                    event_year=self._get_int_attribute(
                        details, "ANO-DE-REALIZACAO"
                    ),
                    event_classification=self._get_attribute(
                        details, "CLASSIFICACAO-DO-EVENTO"
                    ),
                    proceedings_title=self._get_attribute(
                        details, "TITULO-DOS-ANAIS-OU-PROCEEDINGS"
                    ),
                    isbn=self._get_attribute(details, "ISBN"),
                    first_page=self._get_attribute(details, "PAGINA-INICIAL"),
                    last_page=self._get_attribute(details, "PAGINA-FINAL"),
                )
            )

        return conference_papers

    def _get_advisings(self, root: Element) -> list[Advising]:
        advising_levels = {
            "ORIENTACOES-CONCLUIDAS-PARA-MESTRADO": "MESTRADO",
            "ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO": "DOUTORADO",
            "OUTRAS-ORIENTACOES-CONCLUIDAS": "OUTRA",
        }
        advising_elements = root.findall(".//ORIENTACOES-CONCLUIDAS/*")

        advisings: list[Advising] = []
        for advising in advising_elements:
            level = advising_levels.get(advising.tag)
            if level is None:
                continue

            basic_data = self._find_child_with_prefix(advising, "DADOS-BASICOS")
            details = self._find_child_with_prefix(advising, "DETALHAMENTO")
            title = self._get_attribute(basic_data, "TITULO")

            if title is None:
                continue

            advisings.append(
                Advising(
                    level=level,
                    title=title,
                    year=self._get_int_attribute(basic_data, "ANO"),
                    advisee_name=self._get_attribute(details, "NOME-DO-ORIENTADO"),
                    advising_type=self._get_attribute(details, "TIPO-DE-ORIENTACAO"),
                    institution=self._get_attribute(
                        details, "NOME-DA-INSTITUICAO"
                    ),
                    course=self._get_attribute(details, "NOME-DO-CURSO"),
                    country=self._get_attribute(basic_data, "PAIS"),
                    had_scholarship=self._get_bool_attribute(details, "FLAG-BOLSA"),
                    funding_agency=self._get_attribute(details, "NOME-DA-AGENCIA"),
                )
            )

        return advisings

    def extract(self) -> list[XMLData]:
        print("[INFO] Loading...")
        xmls_loaded: list[XMLLoaded] = self.loader.load()

        results: list[XMLData] = []

        print("[INFO] Extracting...")
        for xml_loaded in tqdm(xmls_loaded):
            root: Element[str] | None  = xml_loaded['data'].getroot()

            if root is not None:
                papers: list[Paper] = self._get_papers(root)
                academic_formations = self._get_academic_formations(root)
                research_areas = self._get_research_areas(root)
                conference_papers = self._get_conference_papers(root)
                advisings = self._get_advisings(root)
                researcher_data: ResearcherData = self._get_researcher_data(
                    root,
                    papers,
                    academic_formations,
                    research_areas,
                    conference_papers,
                    advisings,
                )

                results.append(
                    XMLData(
                        researcher_data=researcher_data,
                        filename=xml_loaded['filename'],
                        filehash=xml_loaded['filehash']
                    )
                )

        return results
