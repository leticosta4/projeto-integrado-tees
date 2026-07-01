def _create_researcher(client):
    resp = client.post("/researchers", json={
        "full_name": "Formation Researcher",
        "filename": "f.xml",
        "filehash": "formation_hash",
        "lattes_id": "8888888888888888",
    })
    return resp.get_json()["id"]


def test_create_academic_formation(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "DOUTORADO",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["level"] == "DOUTORADO"
    assert data["researcher_id"] == researcher_id
    assert "id" in data


def test_create_academic_formation_missing_fields(client):
    resp = client.post("/academic-formations", json={"researcher_id": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_create_academic_formation_empty_body(client):
    resp = client.post("/academic-formations", json={})
    assert resp.status_code == 400


def test_list_academic_formations(client):
    researcher_id = _create_researcher(client)
    client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "MESTRADO",
    })
    resp = client.get("/academic-formations")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1


def test_get_academic_formation(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "GRADUACAO",
    })
    formation_id = create_resp.get_json()["id"]

    resp = client.get(f"/academic-formations/{formation_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["level"] == "GRADUACAO"


def test_get_academic_formation_not_found(client):
    resp = client.get("/academic-formations/99999")
    assert resp.status_code == 404


def test_patch_academic_formation(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "ESPECIALIZACAO",
    })
    formation_id = create_resp.get_json()["id"]

    resp = client.patch(f"/academic-formations/{formation_id}", json={"level": "APERFEICOAMENTO"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["level"] == "APERFEICOAMENTO"


def test_patch_academic_formation_not_found(client):
    resp = client.patch("/academic-formations/99999", json={"level": "Ghost"})
    assert resp.status_code == 404


def test_delete_academic_formation(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "POS_DOUTORADO",
    })
    formation_id = create_resp.get_json()["id"]

    resp = client.delete(f"/academic-formations/{formation_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/academic-formations/{formation_id}")
    assert get_resp.status_code == 404


def test_delete_academic_formation_not_found(client):
    resp = client.delete("/academic-formations/99999")
    assert resp.status_code == 404


def test_create_academic_formation_with_all_fields(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "DOUTORADO",
        "institution": "USP",
        "course": "Ciência da Computação",
        "status": "CONCLUIDO",
        "start_year": 2018,
        "end_year": 2022,
        "thesis_title": "Tese de Doutorado",
        "advisor": "Prof. Orientador",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["institution"] == "USP"
    assert data["start_year"] == 2018
    assert data["end_year"] == 2022


def test_list_academic_formations_with_filters(client):
    researcher_id = _create_researcher(client)
    client.post("/academic-formations", json={
        "researcher_id": researcher_id,
        "level": "MESTRADO",
    })
    resp = client.get("/academic-formations?level=MESTRADO")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(f["level"] == "MESTRADO" for f in data)
