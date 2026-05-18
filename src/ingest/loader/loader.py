from pathlib import Path
from ingest.file_lister import FileLister
from xml.etree.ElementTree import ElementTree, Element
from xml.etree.ElementTree import parse
from ingest.loader.models import XMLLoaded
import hashlib

class Loader:
    def __init__(self) -> None:
        self.file_lister: FileLister = FileLister()

    def load(self) -> list[XMLLoaded]:
        files: list[Path] = self.file_lister.list()

        xmls_loaded: list[XMLLoaded] = []
        for file in files:
            filename: str = file.name
            tree: ElementTree = parse(source=file) # ty: ignore
            with open(file, 'rb') as f:
                filehash = hashlib.md5(f.read()).hexdigest()

            xmls_loaded.append(
                XMLLoaded(
                    filename=filename,
                    filehash=filehash,
                    data=tree
                )
            )

        return xmls_loaded
