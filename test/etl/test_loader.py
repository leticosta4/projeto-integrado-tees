from ingest.loader.loader import Loader
from ingest.loader.models import XMLLoaded
from xml.etree.ElementTree import ElementTree, Element

def test_loader():
    loader: Loader = Loader()
    trees: list[XMLLoaded] = loader.load()

    assert trees is not None
    assert isinstance(trees, list)
    assert all(isinstance(x, dict) for x in trees)

    assert len(trees) == 8

    filenames = [tree['filename'] for tree in trees]
    assert all(filename is not None for filename in filenames)

    filehashes = [tree['filehash'] for tree in trees]
    assert all(filehash is not None for filehash in filehashes)

    elements = [tree['data'] for tree in trees]
    assert all(element is not None for element in elements)

    assert '1608472474770322.xml' in filenames

    print(trees)
