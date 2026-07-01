class TestSwaggerDocs:
    def test_swagger_docs(self, client):
        resp = client.get("/api/docs")
        assert resp.status_code == 200
        assert resp.mimetype == "text/html"
        assert "swagger-ui" in resp.get_data(as_text=True)


class TestOpenApiJson:
    def test_openapi_json(self, client):
        resp = client.get("/api/openapi.json")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["openapi"] == "3.0.3"
        assert "info" in data
        assert data["info"]["title"] == "Projeto Integrado TEES API"
        assert "paths" in data

    def test_openapi_json_contains_routes(self, client):
        resp = client.get("/api/openapi.json")
        data = resp.get_json()
        paths = data["paths"]
        assert "/researchers" in paths
        assert "/papers" in paths
        assert "/academic-formations" in paths
        assert "/conference-papers" in paths
        assert "/advisings" in paths
        assert "/research-areas" in paths
        assert "/papers/search" in paths
