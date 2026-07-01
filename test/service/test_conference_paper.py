from unittest.mock import MagicMock

import pytest

from models.conference_paper import ConferencePaper
from service.conference_paper import ConferencePaperService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return ConferencePaperService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestRemoveAll:
    def test_remove_all(self, service, mock_repo):
        service.remove_all_conference_papers()
        mock_repo.remove_all.assert_called_once()


class TestAddConferencePaper:
    def test_add_minimal(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.add_conference_paper(
            researcher_id=1, title="Conference Paper"
        )
        assert result == 42
        mock_repo.add.assert_called_once_with(
            1, "Conference Paper",
            None, None, None, None, None,
            None, None, None, None, None, None, None, None,
        )

    def test_add_with_all_fields(self, service, mock_repo):
        mock_repo.add.return_value = 42
        service.add_conference_paper(
            researcher_id=1,
            title="Full Paper",
            year=2024,
            nature="COMPLETO",
            country="Brasil",
            language="Português",
            doi="10.1234/conf",
            event_name="Evento",
            event_city="São Paulo",
            event_year=2024,
            event_classification="INTERNACIONAL",
            proceedings_title="Anais",
            isbn="978-85-1234",
            first_page="10",
            last_page="20",
        )
        mock_repo.add.assert_called_once_with(
            1, "Full Paper",
            2024, "COMPLETO", "Brasil", "Português",
            "10.1234/conf", "Evento", "São Paulo", 2024,
            "INTERNACIONAL", "Anais", "978-85-1234", "10", "20",
        )


class TestGetCount:
    def test_get_count(self, service, mock_repo):
        mock_repo.count.return_value = 4
        result = service.get_conference_paper_count()
        assert result == 4


class TestGetResearcherLinkCount:
    def test_get_link_count(self, service, mock_repo):
        mock_repo.count_researcher_links.return_value = 6
        result = service.get_conference_paper_researcher_link_count()
        assert result == 6


class TestGetByResearcherId:
    def test_get_by_researcher_id(self, service, mock_repo):
        papers = [
            ConferencePaper(id=1, researcher_id=1, title="Paper 1")
        ]
        mock_repo.get_by_researcher_id.return_value = papers
        result = service.get_conference_papers_by_researcher_id(1)
        assert result == papers


class TestListAll:
    def test_list_all(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        result = service.list_all({"year": 2024})
        assert result == []
        mock_repo.list_all.assert_called_once_with({"year": 2024})

    def test_list_all_no_filters(self, service, mock_repo):
        service.list_all()
        mock_repo.list_all.assert_called_once_with(None)


class TestGetById:
    def test_get_by_id_found(self, service, mock_repo):
        paper = ConferencePaper(id=1, researcher_id=1, title="Test")
        mock_repo.get_by_id.return_value = paper
        result = service.get_by_id(1)
        assert result == paper

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_by_id(999)
        assert result is None


class TestPatch:
    def test_patch(self, service, mock_repo):
        paper = ConferencePaper(id=1, researcher_id=1, title="Updated")
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
