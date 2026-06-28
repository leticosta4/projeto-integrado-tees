from collections.abc import Mapping
from types import UnionType
from typing import Any, TypeVar, Union, get_args, get_origin

from psycopg import sql
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def _unwrap_optional(annotation: Any) -> Any:
    if get_origin(annotation) in (Union, UnionType):
        non_none_args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]
    return annotation


def _coerce_filter_value(
    model: type[BaseModel],
    field: str,
    value: Any,
) -> tuple[Any, bool]:
    field_info = model.model_fields.get(field)
    field_type = _unwrap_optional(field_info.annotation) if field_info else None

    if field_type is bool:
        if isinstance(value, bool):
            return value, True
        normalized = str(value).strip().lower()
        if normalized in ("true", "1", "t", "yes"):
            return True, True
        if normalized in ("false", "0", "f", "no"):
            return False, True
        raise ValueError(f"Invalid boolean value for filter '{field}': {value!r}")

    if field_type in (int, float):
        return field_type(value), True

    return value, False


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

        try:
            coerced_value, exact_match = _coerce_filter_value(model, field, value)
        except (TypeError, ValueError):
            continue

        if exact_match:
            conditions.append(sql.SQL("{} = %s").format(sql.Identifier(field)))
            values.append(coerced_value)
        else:
            conditions.append(sql.SQL("{} ILIKE %s").format(sql.Identifier(field)))
            values.append(f"%{coerced_value}%")

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