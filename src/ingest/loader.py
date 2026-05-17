from pathlib import Path
from ingest.file_lister import FileLister
from xml.etree.ElementTree import ElementTree, Element
from xml.etree.ElementTree import parse

class Loader:
    def __init__(self) -> None:
        self.file_lister: FileLister = FileLister()

    def load(self) -> list[ElementTree]:
        files: list[Path] = self.file_lister.list()

        trees: list[ElementTree] = []
        for file in files:
            tree: ElementTree[Element[str]] = parse(source=file)
            trees.append(tree) # ty: ignore

        return trees
