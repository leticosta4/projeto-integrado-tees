from pathlib import Path
from ingest.file_lister import FileLister


def test_file_lister():
    file_lister: FileLister = FileLister()

    files = file_lister.list()
    assert files is not None
    assert isinstance(files, list)
    assert all(isinstance(x, Path) for x in files)
    assert len(files) == 8
