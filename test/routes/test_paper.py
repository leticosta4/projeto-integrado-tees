def _create_researcher(client):
    resp = client.post("/researchers", json={
        "full_name": "Paper Author",
        "filename": "p.xml",
        "filehash": "paper_hash",
        "lattes_id": "9999999999999999",
    })
    return resp.get_json()["id"]


def test_create_paper(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/papers", json={
        "title": "Test Paper",
        "researcher_id": researcher_id,
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test Paper"
    assert data["researcher_id"] == researcher_id
    assert "id" in data


def test_create_paper_missing_fields(client):
    resp = client.post("/papers", json={"title": "Incomplete"})
    assert resp.status_code == 400


def test_create_paper_empty_body(client):
    resp = client.post("/papers", json={})
    assert resp.status_code == 400


def test_list_papers(client):
    researcher_id = _create_researcher(client)
    client.post("/papers", json={"title": "Paper A", "researcher_id": researcher_id})
    client.post("/papers", json={"title": "Paper B", "researcher_id": researcher_id})
    resp = client.get("/papers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 2


def test_get_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/papers", json={
        "title": "Specific Paper",
        "researcher_id": researcher_id,
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.get(f"/papers/{paper_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Specific Paper"


def test_get_paper_not_found(client):
    resp = client.get("/papers/99999")
    assert resp.status_code == 404


def test_patch_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/papers", json={
        "title": "Original Title",
        "researcher_id": researcher_id,
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.patch(f"/papers/{paper_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated Title"


def test_patch_paper_not_found(client):
    resp = client.patch("/papers/99999", json={"title": "Ghost"})
    assert resp.status_code == 404


def test_delete_paper(client):
    researcher_id = _create_researcher(client)
    create_resp = client.post("/papers", json={
        "title": "Deletable Paper",
        "researcher_id": researcher_id,
    })
    paper_id = create_resp.get_json()["id"]

    resp = client.delete(f"/papers/{paper_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/papers/{paper_id}")
    assert get_resp.status_code == 404


def test_delete_paper_not_found(client):
    resp = client.delete("/papers/99999")
    assert resp.status_code == 404


def test_search_papers(client):
    researcher_id = _create_researcher(client)
    client.post("/papers", json={
        "title": "Machine Learning in Healthcare",
        "researcher_id": researcher_id,
    })
    client.post("/papers", json={
        "title": "Deep Learning for NLP",
        "researcher_id": researcher_id,
    })

    resp = client.get("/papers/search?q=Machine")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) > 0


def test_search_papers_missing_query(client):
    resp = client.get("/papers/search")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_search_papers_invalid_limit(client):
    resp = client.get("/papers/search?q=test&limit=abc")
    assert resp.status_code == 400


def test_create_paper_with_all_fields(client):
    researcher_id = _create_researcher(client)
    resp = client.post("/papers", json={
        "title": "Full Paper",
        "researcher_id": researcher_id,
        "year": 2024,
        "doi": "10.1234/test",
        "journal": "Test Journal",
        "volume": "10",
        "issue": "2",
        "first_page": "100",
        "last_page": "200",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["doi"] == "10.1234/test"
    assert data["year"] == 2024
    assert data["journal"] == "Test Journal"


def test_list_papers_with_filters(client):
    researcher_id = _create_researcher(client)
    client.post("/papers", json={
        "title": "Filtered Paper",
        "researcher_id": researcher_id,
        "year": 2023,
    })
    resp = client.get("/papers?year=2023")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(p["year"] == 2023 for p in data)
