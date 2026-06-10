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
