from psycopg_pool import ConnectionPool

from repository.search import SearchRepository


class SearchService:
    def __init__(self, pool: ConnectionPool) -> None:
        self.repository: SearchRepository = SearchRepository(pool)


    def search(
        self,
        query: str,
        types: set[str],
        result_kinds: set[str],
        limit: int,
        offset: int = 0,
        year_from: int | None = None,
        year_to: int | None = None,
        area: str | None = None,
        researcher_id: int | None = None,
    ) -> list[dict[str, object]]:
        return self.repository.search(
            query,
            types,
            result_kinds,
            limit,
            offset,
            year_from,
            year_to,
            area,
            researcher_id,
        )
