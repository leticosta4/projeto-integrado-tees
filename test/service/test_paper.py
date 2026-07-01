from unittest.mock import MagicMock, patch

import pytest

from models.paper import Paper
from service.paper import PaperService
from embeddings import LocalEmbeddings


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def embeddings():
    return MagicMock()


@pytest.fixture
def service(mock_pool, embeddings):
    return PaperService(mock_pool, embeddings)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestConstructor:
    def test_default_embeddings(self, mock_pool):
        service = PaperService(mock_pool)
        assert service.embeddings_model is not None

    def test_custom_embeddings(self, mock_pool):
        embeddings = MagicMock()
        service = PaperService(mock_pool, embeddings)
        assert service.embeddings_model == embeddings


class TestRemoveAll:
    def test_remove_all(self, service, mock_repo):
        service.remove_all_papers()
        mock_repo.remove_all.assert_called_once()


class TestAddPaper:
    def test_add_paper_minimal(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.add_paper(title="Test Paper", researcher_id=1)
        assert result == 42
        mock_repo.add.assert_called_once_with(
            "Test Paper", 1,
            None, None, None, None, None, None, None, None, None, None, None, None,
        )

    def test_add_paper_with_all_fields(self, service, mock_repo):
        mock_repo.add.return_value = 42
        service.add_paper(
            title="Full Paper",
            researcher_id=1,
            year=2024,
            doi="10.1234/test",
            journal="Test Journal",
            volume="10",
            issue="2",
            first_page="100",
            last_page="200",
        )
        mock_repo.add.assert_called_once_with(
            "Full Paper", 1,
            2024, "10.1234/test",
            None, None, None, "Test Journal",
            None, "10", "2", "100", "200", None,
        )


class TestInsertPaper:
    def test_insert_paper(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.insert_paper(title="Inserted", researcher_id=1)
        assert result == 42


class TestGetPaperCount:
    def test_get_paper_count(self, service, mock_repo):
        mock_repo.count.return_value = 10
        result = service.get_paper_count()
        assert result == 10
        mock_repo.count.assert_called_once()


class TestGetPaperResearcherLinkCount:
    def test_get_link_count(self, service, mock_repo):
        mock_repo.count_researcher_links.return_value = 5
        result = service.get_paper_researcher_link_count()
        assert result == 5
        mock_repo.count_researcher_links.assert_called_once()


class TestGetPaperByTitle:
    def test_get_by_title_found(self, service, mock_repo):
        paper = Paper(id=1, title="Test", researcher_id=1)
        mock_repo.get_by_title.return_value = paper
        result = service.get_paper_by_title("Test")
        assert result == paper
        mock_repo.get_by_title.assert_called_once_with("Test")

    def test_get_by_title_not_found(self, service, mock_repo):
        mock_repo.get_by_title.return_value = None
        result = service.get_paper_by_title("Unknown")
        assert result is None


class TestHybridSearch:
    def test_hybrid_search(self, service, mock_repo, embeddings):
        embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_repo.search.return_value = [
            (Paper(id=1, title="Result 1", researcher_id=1), 0.95),
        ]
        results = service.hybrid_search("test query", 5)
        assert len(results) == 1
        assert results[0][0].title == "Result 1"
        assert results[0][1] == 0.95
        embeddings.embed_query.assert_called_once_with("test query")
        mock_repo.search.assert_called_once_with("test query", [0.1, 0.2, 0.3], 5)

    def test_hybrid_search_uses_local_embeddings(self, mock_pool):
        service = PaperService(mock_pool)
        service.repository = MagicMock()
        service.repository.search.return_value = []
        result = service.hybrid_search("test", 10)
        assert result == []


class TestListAll:
    def test_list_all(self, service, mock_repo):
        papers = [Paper(id=1, title="Paper 1", researcher_id=1)]
        mock_repo.list_all.return_value = papers
        result = service.list_all({"year": 2024})
        assert result == papers
        mock_repo.list_all.assert_called_once_with({"year": 2024})

    def test_list_all_no_filters(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        service.list_all()
        mock_repo.list_all.assert_called_once_with(None)


class TestGetById:
    def test_get_by_id_found(self, service, mock_repo):
        paper = Paper(id=1, title="Test", researcher_id=1)
        mock_repo.get_by_id.return_value = paper
        result = service.get_by_id(1)
        assert result == paper

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_by_id(999)
        assert result is None


class TestPatch:
    def test_patch(self, service, mock_repo):
        paper = Paper(id=1, title="Updated", researcher_id=1)
        mock_repo.patch.return_value = paper
        result = service.patch(1, {"title": "Updated"})
        assert result == paper

    def test_patch_not_found(self, service, mock_repo):
        mock_repo.patch.return_value = None
        result = service.patch(999, {"title": "Ghost"})
        assert result is None


class TestRemoveById:
    def test_remove_by_id(self, service, mock_repo):
        mock_repo.remove_by_id.return_value = 1
        result = service.remove_by_id(1)
        assert result == 1

    def test_remove_by_id_not_found(self, service, mock_repo):
        mock_repo.remove_by_id.return_value = 0
        result = service.remove_by_id(999)
        assert result == 0
