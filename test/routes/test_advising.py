def _create_researcher(client):
    resp = client.post("/researchers", json={
        "full_name": "Advisor Researcher",
        "filename": "adv.xml",
        "filehash": "advising_hash",
        "lattes_id": "7777777777777777",
    })
    return resp.get_json()["id"]


def test_create_advising(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "DOUTORADO",
        "title": "Tese de Doutorado",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["level"] == "DOUTORADO"
    assert data["title"] == "Tese de Doutorado"
    assert data["researcher_id"] == researcher_id
    assert "id" in data


def test_create_advising_missing_fields(client):
    resp = client.post("/advisings", json={"researcher_id": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_create_advising_empty_body(client):
    resp = client.post("/advisings", json={})
    assert resp.status_code == 400


def test_list_advisings(client):
    researcher_id = _create_researcher(client)
    client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "MESTRADO",
        "title": "Dissertação de Mestrado",
    })
    resp = client.get("/advisings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1


def test_get_advising(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "GRADUACAO",
        "title": "TCC",
    })
    advising_id = create_resp.get_json()["id"]

    resp = client.get(f"/advisings/{advising_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "TCC"


def test_get_advising_not_found(client):
    resp = client.get("/advisings/99999")
    assert resp.status_code == 404


def test_patch_advising(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "DOUTORADO",
        "title": "Original Title",
    })
    advising_id = create_resp.get_json()["id"]

    resp = client.patch(f"/advisings/{advising_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated Title"


def test_patch_advising_not_found(client):
    resp = client.patch("/advisings/99999", json={"title": "Ghost"})
    assert resp.status_code == 404


def test_delete_advising(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "POS_DOUTORADO",
        "title": "Deletable Advising",
    })
    advising_id = create_resp.get_json()["id"]

    resp = client.delete(f"/advisings/{advising_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/advisings/{advising_id}")
    assert get_resp.status_code == 404


def test_delete_advising_not_found(client):
    resp = client.delete("/advisings/99999")
    assert resp.status_code == 404


def test_create_advising_with_all_fields(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "DOUTORADO",
        "title": "Tese Completa",
        "year": 2023,
        "advisee_name": "Aluno Teste",
        "advising_type": "ORIENTADOR_PRINCIPAL",
        "institution": "UNICAMP",
        "course": "Computação",
        "country": "Brasil",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["year"] == 2023
    assert data["advisee_name"] == "Aluno Teste"


def test_list_advisings_with_filters(client):
    researcher_id = _create_researcher(client)
    client.post("/advisings", json={
        "researcher_id": researcher_id,
        "level": "MESTRADO",
        "title": "Filtrável",
    })
    resp = client.get("/advisings?level=MESTRADO")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(a["level"] == "MESTRADO" for a in data)
