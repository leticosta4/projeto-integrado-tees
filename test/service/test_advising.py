from unittest.mock import MagicMock

import pytest

from models.advising import Advising
from service.advising import AdvisingService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return AdvisingService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestRemoveAll:
    def test_remove_all(self, service, mock_repo):
        service.remove_all_advisings()
        mock_repo.remove_all.assert_called_once()


class TestAddAdvising:
    def test_add_minimal(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.add_advising(
            researcher_id=1, level="DOUTORADO", title="Tese"
        )
        assert result == 42
        mock_repo.add.assert_called_once_with(
            1, "DOUTORADO", "Tese",
            None, None, None, None, None, None, None, None,
        )

    def test_add_with_all_fields(self, service, mock_repo):
        mock_repo.add.return_value = 42
        service.add_advising(
            researcher_id=1,
            level="MESTRADO",
            title="Dissertação",
            year=2023,
            advisee_name="Aluno",
            advising_type="ORIENTADOR_PRINCIPAL",
            institution="UNICAMP",
            course="Computação",
            country="Brasil",
            had_scholarship=True,
            funding_agency="FAPESP",
        )
        mock_repo.add.assert_called_once_with(
            1, "MESTRADO", "Dissertação",
            2023, "Aluno", "ORIENTADOR_PRINCIPAL",
            "UNICAMP", "Computação", "Brasil", True, "FAPESP",
        )


class TestGetCount:
    def test_get_count(self, service, mock_repo):
        mock_repo.count.return_value = 7
        result = service.get_advising_count()
        assert result == 7


class TestGetByResearcherId:
    def test_get_by_researcher_id(self, service, mock_repo):
        advisings = [
            Advising(id=1, researcher_id=1, level="DOUTORADO", title="Tese")
        ]
        mock_repo.get_by_researcher_id.return_value = advisings
        result = service.get_advisings_by_researcher_id(1)
        assert result == advisings
        mock_repo.get_by_researcher_id.assert_called_once_with(1)


class TestListAll:
    def test_list_all(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        result = service.list_all({"level": "MESTRADO"})
        assert result == []
        mock_repo.list_all.assert_called_once_with({"level": "MESTRADO"})

    def test_list_all_no_filters(self, service, mock_repo):
        service.list_all()
        mock_repo.list_all.assert_called_once_with(None)


class TestGetById:
    def test_get_by_id_found(self, service, mock_repo):
        advising = Advising(id=1, researcher_id=1, level="DOUTORADO", title="Tese")
        mock_repo.get_by_id.return_value = advising
        result = service.get_by_id(1)
        assert result == advising

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_by_id(999)
        assert result is None


class TestPatch:
    def test_patch(self, service, mock_repo):
        advising = Advising(
            id=1, researcher_id=1, level="DOUTORADO", title="Updated"
        )
        mock_repo.patch.return_value = advising
        result = service.patch(1, {"title": "Updated"})
        assert result == advising

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
