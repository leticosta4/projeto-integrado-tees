from unittest.mock import MagicMock, patch

import pytest

from models.researcher import Researcher
from service.researcher import ResearcherService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return ResearcherService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestRemoveAll:
    def test_remove_all(self, service, mock_repo):
        service.remove_all_researchers()
        mock_repo.remove_all.assert_called_once()


class TestCreateResearcher:
    def test_create_researcher(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.create_researcher(
            full_name="John Doe",
            filename="lattes.xml",
            filehash="abc123",
            lattes_id="1234567890123456",
        )
        assert result == 42
        mock_repo.add.assert_called_once_with(
            "John Doe",
            "lattes.xml",
            "abc123",
            "1234567890123456",
            None, None, None, None, None, None,
        )

    def test_create_researcher_with_optionals(self, service, mock_repo):
        mock_repo.add.return_value = 42
        service.create_researcher(
            full_name="John Doe",
            filename="lattes.xml",
            filehash="abc123",
            lattes_id="1234567890123456",
            citation_name="John D.",
            orcid="0000-0001-2345-6789",
            nationality="Brazilian",
        )
        mock_repo.add.assert_called_once_with(
            "John Doe",
            "lattes.xml",
            "abc123",
            "1234567890123456",
            "John D.",
            "0000-0001-2345-6789",
            "Brazilian",
            None, None, None,
        )


class TestGetResearcherCount:
    def test_get_researcher_count(self, service, mock_repo):
        mock_repo.count.return_value = 5
        result = service.get_researcher_count()
        assert result == 5
        mock_repo.count.assert_called_once()


class TestGetResearcherByName:
    def test_get_by_name_found(self, service, mock_repo):
        researcher = Researcher(
            id=1, full_name="John Doe", lattes_id="1234567890123456"
        )
        mock_repo.get_by_full_name.return_value = researcher
        result = service.get_researcher_by_name("John Doe")
        assert result == researcher
        mock_repo.get_by_full_name.assert_called_once_with("John Doe")

    def test_get_by_name_not_found(self, service, mock_repo):
        mock_repo.get_by_full_name.return_value = None
        result = service.get_researcher_by_name("Unknown")
        assert result is None


class TestGetResearcherFilehash:
    def test_get_filehash_found(self, service, mock_repo):
        mock_repo.select_filehash_exists.return_value = "abc123"
        result = service.get_researcher_filehash("abc123")
        assert result == "abc123"
        mock_repo.select_filehash_exists.assert_called_once_with("abc123")

    def test_get_filehash_not_found(self, service, mock_repo):
        mock_repo.select_filehash_exists.return_value = None
        result = service.get_researcher_filehash("nonexistent")
        assert result is None


class TestListAll:
    def test_list_all(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        result = service.list_all({"full_name": "John"})
        assert result == []
        mock_repo.list_all.assert_called_once_with({"full_name": "John"})

    def test_list_all_no_filters(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        result = service.list_all()
        assert result == []
        mock_repo.list_all.assert_called_once_with(None)


class TestGetById:
    def test_get_by_id_found(self, service, mock_repo):
        researcher = Researcher(
            id=1, full_name="John Doe", lattes_id="1234567890123456"
        )
        mock_repo.get_by_id.return_value = researcher
        result = service.get_by_id(1)
        assert result == researcher
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_by_id(999)
        assert result is None


class TestPatch:
    def test_patch(self, service, mock_repo):
        researcher = Researcher(
            id=1, full_name="Updated Name", lattes_id="1234567890123456"
        )
        mock_repo.patch.return_value = researcher
        result = service.patch(1, {"full_name": "Updated Name"})
        assert result == researcher
        mock_repo.patch.assert_called_once_with(1, {"full_name": "Updated Name"})

    def test_patch_not_found(self, service, mock_repo):
        mock_repo.patch.return_value = None
        result = service.patch(999, {"full_name": "Ghost"})
        assert result is None


class TestRemoveById:
    def test_remove_by_id(self, service, mock_repo):
        mock_repo.remove_by_id.return_value = 1
        result = service.remove_by_id(1)
        assert result == 1
        mock_repo.remove_by_id.assert_called_once_with(1)

    def test_remove_by_id_not_found(self, service, mock_repo):
        mock_repo.remove_by_id.return_value = 0
        result = service.remove_by_id(999)
        assert result == 0
