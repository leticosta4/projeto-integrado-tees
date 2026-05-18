from ingest.extractor.extractor import Extractor
from ingest.extractor.models import XMLData, ResearcherData, Paper

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
