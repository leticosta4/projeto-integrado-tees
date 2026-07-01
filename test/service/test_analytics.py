from unittest.mock import MagicMock

import pytest

from service.analytics import AnalyticsService


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def service(mock_pool):
    return AnalyticsService(mock_pool)


@pytest.fixture
def mock_repo(service):
    service.repository = MagicMock()
    return service.repository


class TestSummary:
    def test_summary(self, service, mock_repo):
        mock_repo.summary.return_value = {
            "total_researchers": 10,
            "total_unique_publications": 25,
            "total_authorships": 40,
        }
        result = service.summary(
            types={"paper", "conference_paper"},
            year_from=2020,
            year_to=2024,
            area="Computação",
        )
        assert result["total_researchers"] == 10
        mock_repo.summary.assert_called_once_with(
            {"paper", "conference_paper"}, 2020, 2024, "Computação"
        )

    def test_summary_defaults(self, service, mock_repo):
        service.summary(types={"paper"})
        mock_repo.summary.assert_called_once_with(
            {"paper"}, None, None, None
        )


class TestPublicationsByYear:
    def test_publications_by_year(self, service, mock_repo):
        mock_repo.publications_by_year.return_value = [
            {"year": 2023, "type": "paper", "unique_publications": 5},
        ]
        result = service.publications_by_year(
            types={"paper"}, year_from=2023
        )
        assert len(result) == 1
        assert result[0]["year"] == 2023
        mock_repo.publications_by_year.assert_called_once_with(
            {"paper"}, 2023, None, None
        )


class TestPublicationsByArea:
    def test_publications_by_area(self, service, mock_repo):
        mock_repo.publications_by_area.return_value = [
            {"area": "Computação", "unique_publications": 10},
        ]
        result = service.publications_by_area(
            types={"paper", "advising"}, limit=5
        )
        assert len(result) == 1
        mock_repo.publications_by_area.assert_called_once_with(
            {"paper", "advising"}, None, None, None, 5
        )


class TestTopResearchers:
    def test_top_researchers(self, service, mock_repo):
        mock_repo.top_researchers.return_value = [
            {"researcher_id": 1, "full_name": "Ana", "unique_publications": 15},
        ]
        result = service.top_researchers(
            types={"paper"}, limit=8
        )
        assert len(result) == 1
        mock_repo.top_researchers.assert_called_once_with(
            {"paper"}, None, None, None, 8
        )


class TestCoauthorNetwork:
    def test_coauthor_network(self, service, mock_repo):
        mock_repo.coauthor_network.return_value = {
            "nodes": [{"id": 1, "name": "Ana"}],
            "links": [],
        }
        result = service.coauthor_network(
            types={"paper", "conference_paper"}
        )
        assert "nodes" in result
        mock_repo.coauthor_network.assert_called_once_with(
            {"paper", "conference_paper"}, None, None, None, 50
        )

    def test_coauthor_network_with_limit(self, service, mock_repo):
        service.coauthor_network(
            types={"paper"}, limit=30
        )
        mock_repo.coauthor_network.assert_called_once_with(
            {"paper"}, None, None, None, 30
        )


class TestExportResearchersCSV:
    def test_export_researchers_csv(self, service, mock_repo):
        mock_repo.top_researchers.return_value = [
            {
                "researcher_id": 1,
                "full_name": "Ana",
                "unique_publications": 5,
                "authorships": 8,
                "collaborative_publications": 3,
            },
        ]
        csv_content = service.export_researchers_csv(
            types={"paper"}, year_from=2023
        )
        assert "researcher_id" in csv_content
        assert "Ana" in csv_content
        assert "5" in csv_content


class TestExportAreasCSV:
    def test_export_areas_csv(self, service, mock_repo):
        mock_repo.publications_by_area.return_value = [
            {
                "area": "Ciência da Computação",
                "unique_publications": 10,
                "authorships": 15,
                "collaborative_publications": 5,
            },
        ]
        csv_content = service.export_areas_csv(
            types={"paper"}
        )
        assert "area" in csv_content
        assert "Ciência da Computação" in csv_content


class TestExportFullReportCSV:
    def test_export_full_report(self, service, mock_repo):
        mock_repo.summary.return_value = {
            "total_researchers": 5,
            "total_unique_publications": 20,
            "total_authorships": 30,
            "collaborative_publications": 10,
            "productions_by_type": {
                "paper": {
                    "unique_publications": 10,
                    "authorships": 15,
                    "collaborative_publications": 5,
                },
            },
        }
        mock_repo.publications_by_year.return_value = []
        mock_repo.publications_by_area.return_value = []
        mock_repo.top_researchers.return_value = []

        csv_content = service.export_full_report_csv(
            types={"paper", "advising"}
        )
        assert "RESUMO" in csv_content
        assert "PRODUCOES POR TIPO" in csv_content
        assert "PRODUCOES POR ANO" in csv_content
        assert "PRODUCOES POR AREA" in csv_content
        assert "PESQUISADORES MAIS PRODUTIVOS" in csv_content
        assert "total_researchers" in csv_content
        assert "5" in csv_content
