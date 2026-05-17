from ingest.loader.loader import Loader
from xml.etree.ElementTree import ElementTree, Element
from ingest.extractor.models import XMLData, ResearcherData, Paper

class Extractor:
    def __init__(self):
        self.loader: Loader = Loader()

    def _get_researcher_name(self, root: Element[str]) -> str:
        dados_gerais: Element[str] | None = root.find('DADOS-GERAIS')

        researcher_name = ""

        if dados_gerais is not None:
            researcher_name = (
                dados_gerais.get("NOME-COMPLETO", "")
            )

        return researcher_name

    def _get_papers(self, root: Element[str]):
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
        trees: list[ElementTree] = self.loader.load()

        results: list[XMLData] = []

        for tree in trees:
            root: Element[str] | None  = tree.getroot()

            if root is not None:
                researcher_name: str = self._get_researcher_name(root)
                papers: list[str] = self._get_papers(root)

                results.append(
                    XMLData(
                        researcher_data=ResearcherData(
                            full_name=researcher_name,
                            papers=[
                                p.title
                                for p in papers
                            ]
                        )
                    )
                )
