from ingest.loader.loader import Loader
from ingest.loader.models import XMLLoaded
from xml.etree.ElementTree import ElementTree, Element

def test_loader():
    loader: Loader = Loader()
    trees: list[XMLLoaded] = loader.load()

    assert trees is not None
    assert isinstance(trees, list)
    assert all(isinstance(x, XMLLoaded) for x in trees)

    assert len(trees) == 8
