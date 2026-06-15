from collections.abc import Callable
from typing import Any

from flask import Blueprint, Response, current_app, jsonify, request
from pydantic import BaseModel


CreateHandler = Callable[[Any, dict[str, Any]], int]


def model_to_dict(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")

    if isinstance(value, list):
        return [model_to_dict(item) for item in value]

    if isinstance(value, tuple):
        return tuple(model_to_dict(item) for item in value)

    return value


def get_json_payload() -> tuple[dict[str, Any] | None, tuple[Response, int] | None]:
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return None, (jsonify({"error": "JSON object body is required"}), 400)

    return payload, None


def validate_required(
    payload: dict[str, Any],
    required_fields: tuple[str, ...],
) -> tuple[Response, int] | None:
    missing = [
        field
        for field in required_fields
        if field not in payload or payload[field] is None
    ]

    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    return None


def make_crud_blueprint(
    name: str,
    url_prefix: str,
    service_key: str,
    create_handler: CreateHandler,
    required_fields: tuple[str, ...],
) -> Blueprint:
    blueprint = Blueprint(name, __name__, url_prefix=url_prefix)

    @blueprint.get("")
    def list_items():
        service = current_app.config[service_key]
        items = service.list_all(request.args.to_dict())
        return jsonify(model_to_dict(items))

    @blueprint.post("")
    def create_item():
        service = current_app.config[service_key]
        payload, error = get_json_payload()

        if error:
            return error

        assert payload is not None
        missing_error = validate_required(payload, required_fields)

        if missing_error:
            return missing_error

        item_id = create_handler(service, payload)
        item = service.get_by_id(item_id)
        response = jsonify(model_to_dict(item) if item else {"id": item_id})
        response.status_code = 201
        response.headers["Location"] = f"{request.path}/{item_id}"
        return response

    @blueprint.get("/<int:item_id>")
    def get_item(item_id: int):
        service = current_app.config[service_key]
        item = service.get_by_id(item_id)

        if item is None:
            return jsonify({"error": "Not found"}), 404

        return jsonify(model_to_dict(item))

    @blueprint.patch("/<int:item_id>")
    def patch_item(item_id: int):
        service = current_app.config[service_key]
        payload, error = get_json_payload()

        if error:
            return error

        assert payload is not None
        item = service.patch(item_id, payload)

        if item is None:
            return jsonify({"error": "Not found"}), 404

        return jsonify(model_to_dict(item))

    @blueprint.delete("/<int:item_id>")
    def delete_item(item_id: int):
        service = current_app.config[service_key]
        removed_count = service.remove_by_id(item_id)

        if removed_count == 0:
            return jsonify({"error": "Not found"}), 404

        return "", 204

    return blueprint
