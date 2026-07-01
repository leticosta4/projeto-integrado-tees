from unittest.mock import MagicMock

import pytest

from models.academic_formation import AcademicFormation
from service.academic_formation import AcademicFormationService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return AcademicFormationService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestRemoveAll:
    def test_remove_all(self, service, mock_repo):
        service.remove_all_academic_formations()
        mock_repo.remove_all.assert_called_once()


class TestAddAcademicFormation:
    def test_add_minimal(self, service, mock_repo):
        mock_repo.add.return_value = 42
        result = service.add_academic_formation(
            researcher_id=1, level="DOUTORADO"
        )
        assert result == 42
        mock_repo.add.assert_called_once_with(
            1, "DOUTORADO",
            None, None, None, None, None, None, None, None, None,
        )

    def test_add_with_all_fields(self, service, mock_repo):
        mock_repo.add.return_value = 42
        service.add_academic_formation(
            researcher_id=1,
            level="MESTRADO",
            institution="USP",
            course="Computação",
            status="CONCLUIDO",
            start_year=2018,
            end_year=2020,
            thesis_title="Dissertação",
            advisor="Prof. X",
            funding_agency="CNPq",
            had_scholarship=True,
        )
        mock_repo.add.assert_called_once_with(
            1, "MESTRADO", "USP", "Computação", "CONCLUIDO",
            2018, 2020, "Dissertação", "Prof. X", "CNPq", True,
        )


class TestGetCount:
    def test_get_count(self, service, mock_repo):
        mock_repo.count.return_value = 3
        result = service.get_academic_formation_count()
        assert result == 3


class TestGetByResearcherId:
    def test_get_by_researcher_id(self, service, mock_repo):
        formations = [
            AcademicFormation(id=1, researcher_id=1, level="GRADUACAO")
        ]
        mock_repo.get_by_researcher_id.return_value = formations
        result = service.get_academic_formations_by_researcher_id(1)
        assert result == formations
        mock_repo.get_by_researcher_id.assert_called_once_with(1)


class TestListAll:
    def test_list_all(self, service, mock_repo):
        mock_repo.list_all.return_value = []
        result = service.list_all({"level": "DOUTORADO"})
        assert result == []
        mock_repo.list_all.assert_called_once_with({"level": "DOUTORADO"})

    def test_list_all_no_filters(self, service, mock_repo):
        service.list_all()
        mock_repo.list_all.assert_called_once_with(None)


class TestGetById:
    def test_get_by_id_found(self, service, mock_repo):
        formation = AcademicFormation(id=1, researcher_id=1, level="DOUTORADO")
        mock_repo.get_by_id.return_value = formation
        result = service.get_by_id(1)
        assert result == formation

    def test_get_by_id_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        result = service.get_by_id(999)
        assert result is None


class TestPatch:
    def test_patch(self, service, mock_repo):
        formation = AcademicFormation(
            id=1, researcher_id=1, level="APERFEICOAMENTO"
        )
        mock_repo.patch.return_value = formation
        result = service.patch(1, {"level": "APERFEICOAMENTO"})
        assert result == formation

    def test_patch_not_found(self, service, mock_repo):
        mock_repo.patch.return_value = None
        result = service.patch(999, {"level": "Ghost"})
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
