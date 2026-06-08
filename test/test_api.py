from flask.testing import FlaskClient


class FakeEmbeddingsModel:
    def embed_query(self, text: str) -> list[float]:
        return [float(len(text))] + [0.0] * 127


def test_researcher_crud_endpoint(client: FlaskClient):
    response = client.post(
        "/api/researchers",
        json={
            "full_name": "Ada Lovelace",
            "filename": "ada.xml",
            "filehash": "hash-ada",
            "lattes_id": "123",
            "nationality": "Brasil",
        },
    )

    assert response.status_code == 201
    researcher_id = response.get_json()["id"]

    response = client.get("/api/researchers?full_name=Ada")
    assert response.status_code == 200
    assert response.get_json()[0]["full_name"] == "Ada Lovelace"

    response = client.patch(
        f"/api/researchers/{researcher_id}",
        json={"birth_state": "BA"},
    )
    assert response.status_code == 200
    assert response.get_json()["birth_state"] == "BA"

    response = client.delete(f"/api/researchers/{researcher_id}")
    assert response.status_code == 200
    assert response.get_json()["deleted"] == 1


def test_paper_endpoint_and_search(client: FlaskClient):
    researcher_response = client.post(
        "/api/researchers",
        json={
            "full_name": "Search Researcher",
            "filename": "search.xml",
            "filehash": "hash-search",
            "lattes_id": "456",
        },
    )
    researcher_id = researcher_response.get_json()["id"]

    response = client.post(
        "/api/papers",
        json={
            "title": "Artificial Intelligence in Healthcare",
            "researcher_id": researcher_id,
            "year": 2026,
            "title_embeddings": [42.0] + [0.0] * 127,
        },
    )
    assert response.status_code == 201

    response = client.get("/api/papers?title=Healthcare")
    assert response.status_code == 200
    assert response.get_json()[0]["title"] == "Artificial Intelligence in Healthcare"

    client.application.config["PAPER_SERVICE"].embeddings_model = FakeEmbeddingsModel()
    response = client.get("/api/papers/search?q=AI%20health&limit=5")
    assert response.status_code == 200
    assert response.get_json()[0]["paper"]["title"] == (
        "Artificial Intelligence in Healthcare"
    )
