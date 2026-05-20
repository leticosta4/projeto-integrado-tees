from app import create_app
from pathlib import Path
from service.researcher import ResearcherService
from service.paper import PaperService

from etl.file_lister import FileLister
from etl.extractor import Extractor
from etl.loader import Loader
from etl.models import XMLData, ResearcherData, XMLLoaded, Paper

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

def test_extractor():
    extractor: Extractor = Extractor()
    results: list[XMLData] = extractor.extract()
    assert results is not None
    assert isinstance(results, list)
    assert all(isinstance(x, XMLData) for x in results)

    assert len(results) == 8

    researchers_data: list[ResearcherData] = [d.researcher_data for d in results]

    full_names: list[str] = [d.full_name for d in researchers_data]
    assert any('Eduardo' in name for name in full_names)

    assert any(
        'experiments' in paper.title
        for researcher in researchers_data
        for paper in researcher.papers
    )

def test_storage(app):
    extractor: Extractor = Extractor()
    data: list[XMLData] = extractor.extract()

    researcher_service: ResearcherService = app.config['RESEARCHER_SERVICE']
    assert researcher_service.get_researcher_count() == 0
    paper_service: PaperService = app.config['PAPER_SERVICE']
    assert paper_service.get_paper_count() == 0

    for xml in data:
        researcher: ResearcherData = xml.researcher_data
        id = researcher_service.add_researcher(researcher.full_name)
        for paper in researcher.papers:
            paper_service.add_paper(paper.title, id)

    assert researcher_service.get_researcher_count() == 8
    assert paper_service.get_paper_count() == 494 
