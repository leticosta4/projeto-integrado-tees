def _create_researcher(client):
    resp = client.post("/researchers", json={
        "full_name": "Conference Researcher",
        "filename": "conf.xml",
        "filehash": "conf_hash",
        "lattes_id": "6666666666666666",
    })
    return resp.get_json()["id"]


def test_create_conference_paper(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Conference Paper Title",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Conference Paper Title"
    assert data["researcher_id"] == researcher_id
    assert "id" in data


def test_create_conference_paper_missing_fields(client):
    resp = client.post("/conference-papers", json={"researcher_id": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_create_conference_paper_empty_body(client):
    resp = client.post("/conference-papers", json={})
    assert resp.status_code == 400


def test_list_conference_papers(client):
    researcher_id = _create_researcher(client)
    client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Paper A",
    })
    resp = client.get("/conference-papers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1


def test_get_conference_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Specific Conference Paper",
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.get(f"/conference-papers/{paper_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Specific Conference Paper"


def test_get_conference_paper_not_found(client):
    resp = client.get("/conference-papers/99999")
    assert resp.status_code == 404


def test_patch_conference_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Original Title",
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.patch(f"/conference-papers/{paper_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated Title"


def test_patch_conference_paper_not_found(client):
    resp = client.patch("/conference-papers/99999", json={"title": "Ghost"})
    assert resp.status_code == 404


def test_delete_conference_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Deletable Paper",
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.delete(f"/conference-papers/{paper_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/conference-papers/{paper_id}")
    assert get_resp.status_code == 404


def test_delete_conference_paper_not_found(client):
    resp = client.delete("/conference-papers/99999")
    assert resp.status_code == 404


def test_create_conference_paper_with_all_fields(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Full Conference Paper",
        "year": 2024,
        "doi": "10.1234/conf",
        "event_name": "International Conference",
        "event_city": "São Paulo",
        "event_year": 2024,
        "country": "Brasil",
        "language": "Português",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["doi"] == "10.1234/conf"
    assert data["event_name"] == "International Conference"
    assert data["year"] == 2024


def test_list_conference_papers_with_filters(client):
    researcher_id = _create_researcher(client)
    client.post("/conference-papers", json={
        "researcher_id": researcher_id,
        "title": "Filtered Paper",
        "year": 2022,
    })
    resp = client.get("/conference-papers?year=2022")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(cp["year"] == 2022 for cp in data)
