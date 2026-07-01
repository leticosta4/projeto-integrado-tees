import csv
import io
from typing import Any

from psycopg_pool import ConnectionPool

from repository.analytics import AnalyticsRepository


class AnalyticsService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: AnalyticsRepository = AnalyticsRepository(pool)


    def summary(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> dict[str, Any]:
        return self.repository.summary(types, year_from, year_to, area)


    def publications_by_year(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.repository.publications_by_year(types, year_from, year_to, area)


    def publications_by_area(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        return self.repository.publications_by_area(
            types,
            year_from,
            year_to,
            area,
            limit,
        )


    def top_researchers(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        return self.repository.top_researchers(types, year_from, year_to, area, limit)


    def coauthor_network(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        limit: int = 50,
    ) -> dict[str, list[dict[str, Any]]]:
        return self.repository.coauthor_network(types, year_from, year_to, area, limit)


    def export_researchers_csv(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> str:
        rows = self.repository.top_researchers(types, year_from, year_to, area, limit=None)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["researcher_id", "full_name", "unique_publications", "authorships", "collaborative_publications"])
        for row in rows:
            writer.writerow([
                row["researcher_id"],
                row["full_name"],
                row["unique_publications"],
                row["authorships"],
                row["collaborative_publications"],
            ])
        return output.getvalue()


    def export_areas_csv(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> str:
        rows = self.repository.publications_by_area(types, year_from, year_to, area, limit=None)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["area", "unique_publications", "authorships", "collaborative_publications"])
        for row in rows:
            writer.writerow([
                row["area"],
                row["unique_publications"],
                row["authorships"],
                row["collaborative_publications"],
            ])
        return output.getvalue()


    def export_full_report_csv(
        self,
        types: set[str],
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
    ) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["=== RESUMO ==="])
        summary = self.repository.summary(types, year_from, year_to, area)
        writer.writerow(["total_researchers", summary.get("total_researchers", 0)])
        writer.writerow(["total_unique_publications", summary.get("total_unique_publications", 0)])
        writer.writerow(["total_authorships", summary.get("total_authorships", 0)])
        writer.writerow(["collaborative_publications", summary.get("collaborative_publications", 0)])
        writer.writerow([])

        writer.writerow(["=== PRODUCOES POR TIPO ==="])
        writer.writerow(["type", "unique_publications", "authorships", "collaborative_publications"])
        for pub_type, values in summary.get("productions_by_type", {}).items():
            writer.writerow([
                pub_type,
                values.get("unique_publications", 0),
                values.get("authorships", 0),
                values.get("collaborative_publications", 0),
            ])
        writer.writerow([])

        writer.writerow(["=== PRODUCOES POR ANO ==="])
        writer.writerow(["year", "type", "unique_publications", "authorships", "collaborative_publications"])
        year_rows = self.repository.publications_by_year(types, year_from, year_to, area)
        for row in year_rows:
            writer.writerow([
                row["year"],
                row["type"],
                row["unique_publications"],
                row["authorships"],
                row["collaborative_publications"],
            ])
        writer.writerow([])

        writer.writerow(["=== PRODUCOES POR AREA ==="])
        writer.writerow(["area", "unique_publications", "authorships", "collaborative_publications"])
        area_rows = self.repository.publications_by_area(types, year_from, year_to, area, limit=None)
        for row in area_rows:
            writer.writerow([
                row["area"],
                row["unique_publications"],
                row["authorships"],
                row["collaborative_publications"],
            ])
        writer.writerow([])

        writer.writerow(["=== PESQUISADORES MAIS PRODUTIVOS ==="])
        writer.writerow(["researcher_id", "full_name", "unique_publications", "authorships", "collaborative_publications"])
        researcher_rows = self.repository.top_researchers(types, year_from, year_to, area, limit=None)
        for row in researcher_rows:
            writer.writerow([
                row["researcher_id"],
                row["full_name"],
                row["unique_publications"],
                row["authorships"],
                row["collaborative_publications"],
            ])

        return output.getvalue()
