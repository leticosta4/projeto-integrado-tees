from flask.testing import FlaskClient


def test_hello_world_page(client: FlaskClient):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Projeto Integrado TEES" in response.data
    assert b"/api/docs" in response.data
    assert b"/api/openapi.json" in response.data
    assert b"/inicio" in response.data


def test_prototype_home_page(client: FlaskClient):
    response = client.get("/inicio")

    assert response.status_code == 200
    assert b"Portal de Pesquisa Lattes" in response.data
    assert b"FILTROS" in response.data
    assert b"Modulo analitico" in response.data
    assert b'data-filter-toggle' in response.data
    assert b'id="filter-panel"' in response.data
    assert b"prototype-home.js" in response.data


def test_prototype_home_search_uses_database(client: FlaskClient):
    researcher_response = client.post(
        "/api/researchers",
        json={
            "full_name": "Ada Lovelace",
            "filename": "ada.xml",
            "filehash": "hash-ada-home-search",
            "lattes_id": "123-home-search",
        },
    )
    researcher_id = researcher_response.get_json()["id"]

    client.post(
        "/api/papers",
        json={
            "title": "Artificial Intelligence in Healthcare",
            "researcher_id": researcher_id,
            "year": 2026,
        },
    )

    response = client.get("/inicio?q=Healthcare")

    assert response.status_code == 200
    assert b"Artificial Intelligence in Healthcare" in response.data
    assert b"Ada Lovelace" in response.data
    assert b"Busca textual" in response.data


def test_health_endpoint(client: FlaskClient):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_openapi_spec_exposes_routes_for_postman_or_swagger(client: FlaskClient):
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    spec = response.get_json()
    assert spec["openapi"] == "3.0.3"
    assert "/api/researchers" in spec["paths"]
    assert "/api/papers/search" in spec["paths"]


def test_swagger_docs_page(client: FlaskClient):
    response = client.get("/api/docs")

    assert response.status_code == 200
    assert b"SwaggerUIBundle" in response.data
    assert b"/api/openapi.json" in response.data
