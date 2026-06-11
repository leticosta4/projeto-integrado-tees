from settings import Settings
from pathlib import Path

from etl.file_lister import FileLister
from etl.loader import Loader
from etl.models import XMLLoaded

def test_file_lister():
    file_lister: FileLister = FileLister()

    files = file_lister.list()
    assert files is not None
    assert isinstance(files, list)
    assert all(isinstance(x, Path) for x in files)
    assert len(files) == 8

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

def test_embeddings():
    settings: Settings = Settings()
    assert settings.EMBEDDING_MODEL is not None
    assert settings.DIMENSIONS > 0
    