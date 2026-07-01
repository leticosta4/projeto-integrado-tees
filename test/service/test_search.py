from unittest.mock import MagicMock

import pytest

from service.search import SearchService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return SearchService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestSearch:
    def test_search_basic(self, service, mock_repo):
        mock_repo.search.return_value = [
            {"result_type": "paper", "id": 1, "title": "Machine Learning"},
        ]
        results = service.search(
            query="machine learning",
            types={"paper"},
            result_kinds={"publications"},
            limit=10,
            offset=0,
        )
        assert len(results) == 1
        assert results[0]["title"] == "Machine Learning"
        mock_repo.search.assert_called_once_with(
            "machine learning",
            {"paper"},
            {"publications"},
            10,
            0,
            None, None, None, None,
        )

    def test_search_with_all_filters(self, service, mock_repo):
        mock_repo.search.return_value = []
        service.search(
            query="deep learning",
            types={"paper", "conference_paper"},
            result_kinds={"publications", "researchers"},
            limit=20,
            offset=5,
            year_from=2020,
            year_to=2024,
            area="Computação",
            researcher_id=1,
        )
        mock_repo.search.assert_called_once_with(
            "deep learning",
            {"paper", "conference_paper"},
            {"publications", "researchers"},
            20,
            5,
            2020, 2024, "Computação", 1,
        )

    def test_search_with_default_offset(self, service, mock_repo):
        mock_repo.search.return_value = []
        service.search(
            query="test",
            types={"paper"},
            result_kinds={"publications"},
            limit=10,
        )
        mock_repo.search.assert_called_once_with(
            "test",
            {"paper"},
            {"publications"},
            10,
            0,
            None, None, None, None,
        )

    def test_search_returns_empty(self, service, mock_repo):
        mock_repo.search.return_value = []
        results = service.search(
            query="nothing",
            types={"paper"},
            result_kinds={"publications"},
            limit=10,
        )
        assert results == []
