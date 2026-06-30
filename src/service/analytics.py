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
