def _seed_data(client):
    r1 = client.post("/researchers", json={
        "full_name": "Ana Pesquisadora",
        "filename": "ana.xml",
        "filehash": "ana_hash",
        "lattes_id": "1111111111111111",
    }).get_json()["id"]

    r2 = client.post("/researchers", json={
        "full_name": "João Pesquisador",
        "filename": "joao.xml",
        "filehash": "joao_hash",
        "lattes_id": "2222222222222222",
    }).get_json()["id"]

    client.post("/papers", json={
        "title": "Paper Ana 1",
        "researcher_id": r1,
        "year": 2023,
    })
    client.post("/papers", json={
        "title": "Paper Ana 2",
        "researcher_id": r1,
        "year": 2024,
    })
    client.post("/papers", json={
        "title": "Paper João 1",
        "researcher_id": r2,
        "year": 2023,
    })

    client.post("/conference-papers", json={
        "title": "Conf Ana",
        "researcher_id": r1,
        "year": 2023,
    })

    client.post("/advisings", json={
        "researcher_id": r1,
        "level": "MESTRADO",
        "title": "Orientação Ana",
        "year": 2024,
    })

    return r1, r2


class TestSummary:
    def test_summary_without_filters(self, client):
        _seed_data(client)
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_researchers" in data
        assert "total_unique_publications" in data
        assert "total_authorships" in data
        assert "productions_by_type" in data

    def test_summary_with_year_filter(self, client):
        _seed_data(client)
        resp = client.get("/analytics/summary?year_from=2023&year_to=2023")
        assert resp.status_code == 200

    def test_summary_with_type_filter(self, client):
        _seed_data(client)
        resp = client.get("/analytics/summary?type=paper")
        assert resp.status_code == 200

    def test_summary_with_invalid_year(self, client):
        resp = client.get("/analytics/summary?year_from=abc")
        assert resp.status_code == 400

    def test_summary_with_invalid_year_to(self, client):
        resp = client.get("/analytics/summary?year_to=xyz")
        assert resp.status_code == 400


class TestPublicationsByYear:
    def test_publications_by_year(self, client):
        _seed_data(client)
        resp = client.get("/analytics/publications-by-year")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_publications_by_year_with_filters(self, client):
        _seed_data(client)
        resp = client.get("/analytics/publications-by-year?year_from=2023")
        assert resp.status_code == 200


class TestPublicationsByArea:
    def test_publications_by_area(self, client):
        _seed_data(client)
        resp = client.get("/analytics/publications-by-area")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_publications_by_area_with_limit(self, client):
        _seed_data(client)
        resp = client.get("/analytics/publications-by-area?limit=5")
        assert resp.status_code == 200

    def test_publications_by_area_invalid_limit(self, client):
        resp = client.get("/analytics/publications-by-area?limit=abc")
        assert resp.status_code == 400


class TestTopResearchers:
    def test_top_researchers(self, client):
        _seed_data(client)
        resp = client.get("/analytics/top-researchers")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_top_researchers_with_limit(self, client):
        _seed_data(client)
        resp = client.get("/analytics/top-researchers?limit=3")
        assert resp.status_code == 200

    def test_top_researchers_invalid_limit(self, client):
        resp = client.get("/analytics/top-researchers?limit=-1")
        assert resp.status_code == 400


class TestCoauthorNetwork:
    def test_coauthor_network(self, client):
        _seed_data(client)
        resp = client.get("/analytics/coauthor-network")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_coauthor_network_with_limit(self, client):
        _seed_data(client)
        resp = client.get("/analytics/coauthor-network?limit=10")
        assert resp.status_code == 200


class TestExportCSV:
    def test_export_researchers_csv(self, client):
        _seed_data(client)
        resp = client.get("/analytics/export/csv?type=researchers")
        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"
        assert "researcher_id" in resp.get_data(as_text=True)

    def test_export_areas_csv(self, client):
        _seed_data(client)
        resp = client.get("/analytics/export/csv?type=areas")
        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"

    def test_export_report_csv(self, client):
        _seed_data(client)
        resp = client.get("/analytics/export/csv?type=report")
        assert resp.status_code == 200
        assert resp.mimetype == "text/csv"
        content = resp.get_data(as_text=True)
        assert "RESUMO" in content

    def test_export_csv_invalid_type(self, client):
        resp = client.get("/analytics/export/csv?type=invalid")
        assert resp.status_code == 400

    def test_export_csv_missing_type(self, client):
        resp = client.get("/analytics/export/csv")
        assert resp.status_code == 400
