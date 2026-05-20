from xml.etree.ElementTree import Element

from etl.loader import Loader
from etl.models import XMLData, ResearcherData, Paper, XMLLoaded

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

    def _get_researcher_data(self, root: Element, papers: list[Paper]) -> ResearcherData:
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

    def extract(self) -> list[XMLData]:
        xmls_loaded: list[XMLLoaded] = self.loader.load()

        results: list[XMLData] = []

        for xml_loaded in xmls_loaded:
            root: Element[str] | None  = xml_loaded['data'].getroot()

            if root is not None:
                papers: list[Paper] = self._get_papers(root)
                researcher_data: ResearcherData = self._get_researcher_data(
                    root,
                    papers,
                )

                results.append(
                    XMLData(
                        researcher_data=researcher_data,
                        filename=xml_loaded['filename'],
                        filehash=xml_loaded['filehash']
                    )
                )

        return results
