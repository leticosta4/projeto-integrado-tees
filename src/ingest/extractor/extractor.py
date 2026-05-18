from ingest.loader.loader import Loader
from xml.etree.ElementTree import ElementTree, Element
from ingest.extractor.models import XMLData, ResearcherData, Paper
from ingest.loader.models import XMLLoaded

class Extractor:
    def __init__(self):
        self.loader: Loader = Loader()

    def _get_researcher_name(self, root: Element) -> str:
        dados_gerais: Element[str] | None = root.find('DADOS-GERAIS')

        researcher_name = ""

        if dados_gerais is not None:
            researcher_name = (
                dados_gerais.get("NOME-COMPLETO", "")
            )

        return researcher_name

    def _get_papers(self, root: Element):
        paper_elements = root.findall(
            ".//ARTIGO-PUBLICADO/DADOS-BASICOS-DO-ARTIGO"
        )

        paper_titles: list[str] = []

        for paper in paper_elements:
            title: str | None = paper.get("TITULO-DO-ARTIGO")

            if title is not None:
                paper_titles.append(title)

        return paper_titles

    def extract(self) -> list[XMLData]:
        xmls_loaded: list[XMLLoaded] = self.loader.load()

        results: list[XMLData] = []

        for xml_loaded in xmls_loaded:
            root: Element[str] | None  = xml_loaded['data'].getroot()

            if root is not None:
                researcher_name: str = self._get_researcher_name(root)
                paper_names: list[str] = self._get_papers(root)

                papers: list[Paper] = [Paper(title=p) for p in paper_names]
                researcher_data: ResearcherData = ResearcherData(
                    full_name=researcher_name,
                    papers=papers
                )

                results.append(
                    XMLData(
                        researcher_data=researcher_data,
                        filename=xml_loaded['filename'],
                        filehash=xml_loaded['filehash']
                    )
                )

        return results
