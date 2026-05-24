from typing import Any

from psycopg_pool import ConnectionPool


class BaseDao:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool: ConnectionPool = pool

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, params)
                return cur.rowcount

    def insert_and_return_id(self, sql: str, params: tuple[Any, ...]) -> int:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, params)
                row = cur.fetchone()
                return row[0] if row else 0

    def fetch_value(self, sql: str, params: tuple[Any, ...] = ()) -> Any | None:
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                _ = cur.execute(sql, params)
                row = cur.fetchone()
                return row[0] if row else None

    def fetch_one(
        self,
        sql: str,
        params: tuple[Any, ...] = (),
        row_factory: Any | None = None,
    ) -> Any | None:
        with self.pool.connection() as conn:
            if row_factory is None:
                with conn.cursor() as cur:
                    _ = cur.execute(sql, params)
                    return cur.fetchone()

            with conn.cursor(row_factory=row_factory) as cur:
                _ = cur.execute(sql, params)
                return cur.fetchone()

    def fetch_all(
        self,
        sql: str,
        params: tuple[Any, ...] = (),
        row_factory: Any | None = None,
    ) -> list[Any]:
        with self.pool.connection() as conn:
            if row_factory is None:
                with conn.cursor() as cur:
                    _ = cur.execute(sql, params)
                    return cur.fetchall()

            with conn.cursor(row_factory=row_factory) as cur:
                _ = cur.execute(sql, params)
                return cur.fetchall()
