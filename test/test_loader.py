from ingest.loader import Loader
from xml.etree.ElementTree import ElementTree, Element

def test_loader():
    loader: Loader = Loader()
    trees: list[ElementTree] = loader.load()

    assert trees is not None
    assert isinstance(trees, list)
    assert all(isinstance(x, ElementTree) for x in trees)

    assert len(trees) == 8
