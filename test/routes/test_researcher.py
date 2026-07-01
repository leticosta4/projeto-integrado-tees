def test_create_researcher(client):
    resp = client.post("/researchers", json={
        "full_name": "John Doe",
        "filename": "lattes.xml",
        "filehash": "abc123",
        "lattes_id": "1234567890123456",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["full_name"] == "John Doe"
    assert data["lattes_id"] == "1234567890123456"
    assert "id" in data


def test_create_researcher_missing_fields(client):
    resp = client.post("/researchers", json={"full_name": "John Doe"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_create_researcher_empty_body(client):
    resp = client.post("/researchers", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_list_researchers(client):
    client.post("/researchers", json={
        "full_name": "Alice",
        "filename": "a.xml",
        "filehash": "aaa",
        "lattes_id": "1111111111111111",
    })
    client.post("/researchers", json={
        "full_name": "Bob",
        "filename": "b.xml",
        "filehash": "bbb",
        "lattes_id": "2222222222222222",
    })
    resp = client.get("/researchers")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 2


def test_get_researcher(client):
    create_resp = client.post("/researchers", json={
        "full_name": "Charlie",
        "filename": "c.xml",
        "filehash": "ccc",
        "lattes_id": "3333333333333333",
    })
    researcher_id = create_resp.get_json()["id"]

    resp = client.get(f"/researchers/{researcher_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["full_name"] == "Charlie"


def test_get_researcher_not_found(client):
    resp = client.get("/researchers/99999")
    assert resp.status_code == 404


def test_patch_researcher(client):
    create_resp = client.post("/researchers", json={
        "full_name": "Diana",
        "filename": "d.xml",
        "filehash": "ddd",
        "lattes_id": "4444444444444444",
    })
    researcher_id = create_resp.get_json()["id"]

    resp = client.patch(f"/researchers/{researcher_id}", json={"full_name": "Diana Updated"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["full_name"] == "Diana Updated"


def test_patch_researcher_not_found(client):
    resp = client.patch("/researchers/99999", json={"full_name": "Ghost"})
    assert resp.status_code == 404


def test_delete_researcher(client):
    create_resp = client.post("/researchers", json={
        "full_name": "Eve",
        "filename": "e.xml",
        "filehash": "eee",
        "lattes_id": "5555555555555555",
    })
    researcher_id = create_resp.get_json()["id"]

    resp = client.delete(f"/researchers/{researcher_id}")
    assert resp.status_code == 204

    get_resp = client.get(f"/researchers/{researcher_id}")
    assert get_resp.status_code == 404


def test_delete_researcher_not_found(client):
    resp = client.delete("/researchers/99999")
    assert resp.status_code == 404


def test_create_researcher_with_optional_fields(client):
    resp = client.post("/researchers", json={
        "full_name": "Frank",
        "filename": "f.xml",
        "filehash": "fff",
        "lattes_id": "6666666666666666",
        "citation_name": "Frank S.",
        "orcid": "0000-0001-2345-6789",
        "nationality": "Brazilian",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["citation_name"] == "Frank S."
    assert data["orcid"] == "0000-0001-2345-6789"


def test_list_researchers_with_filters(client):
    client.post("/researchers", json={
        "full_name": "Grace",
        "filename": "g.xml",
        "filehash": "ggg",
        "lattes_id": "7777777777777777",
    })
    resp = client.get("/researchers?full_name=Grace")
    assert resp.status_code == 200
    data = resp.get_json()
    assert all(r["full_name"] == "Grace" for r in data)
