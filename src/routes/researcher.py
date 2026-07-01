from typing import Any
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
import json

from flask import current_app, jsonify

from routes.crud import make_crud_blueprint, model_to_dict


def create_researcher(service: Any, data: dict[str, Any]) -> int:
    return service.create_researcher(**data)


researcher_bp = make_crud_blueprint(
    "researcher",
    "/researchers",
    "RESEARCHER_SERVICE",
    create_researcher,
    ("full_name", "filename", "filehash", "lattes_id"),
)


def _normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


@researcher_bp.get("/<int:researcher_id>/external-profile")
def get_researcher_external_profile(researcher_id: int):
    service = current_app.config["RESEARCHER_SERVICE"]
    researcher = service.get_by_id(researcher_id)

    if researcher is None:
        return jsonify({"error": "Not found"}), 404

    base_url = "https://oda.vertb.com.br"
    url = f"{base_url}/pesquisadores?nome={quote(researcher.full_name)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "projeto-integrado-tees/0.1",
        },
    )

    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return jsonify({"researcher": model_to_dict(researcher), "external_profile": None})

    candidates = payload.get("data", []) if isinstance(payload, dict) else []
    if not isinstance(candidates, list):
        candidates = []

    external_profile = next(
        (
            candidate
            for candidate in candidates
            if isinstance(candidate, dict)
            and str(candidate.get("lattesId") or "") == researcher.lattes_id
        ),
        None,
    )

    if external_profile is None:
        normalized_name = _normalize_name(researcher.full_name)
        external_profile = next(
            (
                candidate
                for candidate in candidates
                if isinstance(candidate, dict)
                and _normalize_name(str(candidate.get("nome") or "")) == normalized_name
            ),
            None,
        )

    if isinstance(external_profile, dict) and external_profile.get("imageUrl"):
        external_profile["imageUrl"] = urljoin(base_url, str(external_profile["imageUrl"]))

    return jsonify(
        {
            "researcher": model_to_dict(researcher),
            "external_profile": external_profile,
        }
    )
