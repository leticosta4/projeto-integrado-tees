from collections.abc import Mapping
from typing import Any, TypeVar

from psycopg import sql
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def list_all(
    pool: ConnectionPool,
    table: str,
    columns: list[str],
    model: type[ModelT],
    filters: Mapping[str, Any] | None = None,
) -> list[ModelT]:
    allowed_filters = set(columns)
    conditions: list[sql.Composable] = []
    values: list[Any] = []

    for field, value in (filters or {}).items():
        if field not in allowed_filters or value is None or value == "":
            continue

        if isinstance(value, str):
            conditions.append(sql.SQL("{} ILIKE %s").format(sql.Identifier(field)))
            values.append(f"%{value}%")
        else:
            conditions.append(sql.SQL("{} = %s").format(sql.Identifier(field)))
            values.append(value)

    where_clause = (
        sql.SQL("WHERE ") + sql.SQL(" AND ").join(conditions)
        if conditions
        else sql.SQL("")
    )
    query = sql.SQL("""
                SELECT {}
                FROM {}
                {}
                ORDER BY id
                """).format(
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                sql.Identifier(table),
                where_clause,
            )

    with pool.connection() as conn:
        with conn.cursor(row_factory=class_row(model)) as cur:
            _ = cur.execute(query, values)
            return cur.fetchall()
