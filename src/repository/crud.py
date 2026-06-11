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
        
    
def get_by_id(
    pool: ConnectionPool,
    table: str,
    columns: list[str],
    model: type[ModelT],
    item_id: int,
) -> ModelT | None:
    query = sql.SQL("""
    SELECT {}
    FROM {}
    WHERE id = %s
    """).format(
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.Identifier(table),
    )

    with pool.connection() as conn:
        with conn.cursor(row_factory=class_row(model)) as cur:
            _ = cur.execute(query, (item_id,))
            return cur.fetchone()


def patch_by_id(
    pool: ConnectionPool,
    table: str,
    columns: list[str],
    model: type[ModelT],
    item_id: int,
    data: Mapping[str, Any],
) -> ModelT | None:
    editable_columns = [column for column in columns if column != "id"]
    updates = [
        (field, value)
        for field, value in data.items()
        if field in editable_columns
    ]

    if not updates:
        return get_by_id(pool, table, columns, model, item_id)

    set_clause = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(field))
        for field, _ in updates
    )
    values = [value for _, value in updates]
    values.append(item_id)

    query = sql.SQL("""
    UPDATE {}
    SET {}
    WHERE id = %s
    RETURNING {}
    """).format(
        sql.Identifier(table),
        set_clause,
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    with pool.connection() as conn:
        with conn.cursor(row_factory=class_row(model)) as cur:
            _ = cur.execute(query, values)
            return cur.fetchone()


def remove_by_id(pool: ConnectionPool, table: str, item_id: int) -> int:
    query = sql.SQL("""
    DELETE FROM {}
    WHERE id = %s
    """).format(sql.Identifier(table))

    with pool.connection() as conn:
        with conn.cursor() as cur:
            _ = cur.execute(query, (item_id,))
            return cur.rowcount
        