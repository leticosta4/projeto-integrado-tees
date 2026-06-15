from flask import Blueprint, jsonify


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/docs")
def swagger_docs():
    return """
    <!doctype html>
    <html>
      <head>
        <title>Projeto Integrado TEES API</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => {
            window.ui = SwaggerUIBundle({
              url: "/api/openapi.json",
              dom_id: "#swagger-ui",
            });
          };
        </script>
      </body>
    </html>
    """


@api_bp.get("/openapi.json")
def openapi_json():
    return jsonify(
        {
            "openapi": "3.0.3",
            "info": {
                "title": "Projeto Integrado TEES API",
                "version": "1.0.0",
            },
            "paths": {
                **crud_paths("/researchers", "Researcher"),
                **crud_paths("/papers", "Paper"),
                "/papers/search": {
                    "get": {
                        "tags": ["Paper"],
                        "summary": "Search papers",
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer", "default": 10},
                            },
                        ],
                        "responses": {
                            "200": {"description": "Search results"},
                            "400": {"description": "Invalid query parameters"},
                        },
                    }
                },
                **crud_paths("/academic-formations", "AcademicFormation"),
                **crud_paths("/research-areas", "ResearchArea"),
                **crud_paths("/conference-papers", "ConferencePaper"),
                **crud_paths("/advisings", "Advising"),
            },
        }
    )


def crud_paths(path: str, tag: str) -> dict[str, object]:
    return {
        path: {
            "get": {
                "tags": [tag],
                "summary": f"List {tag} records",
                "responses": {"200": {"description": "Records returned"}},
            },
            "post": {
                "tags": [tag],
                "summary": f"Create {tag} record",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Record created"},
                    "400": {"description": "Invalid payload"},
                },
            },
        },
        f"{path}/{{item_id}}": {
            "get": {
                "tags": [tag],
                "summary": f"Get {tag} record by id",
                "parameters": [item_id_parameter()],
                "responses": {
                    "200": {"description": "Record returned"},
                    "404": {"description": "Record not found"},
                },
            },
            "patch": {
                "tags": [tag],
                "summary": f"Update {tag} record",
                "parameters": [item_id_parameter()],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Record updated"},
                    "400": {"description": "Invalid payload"},
                    "404": {"description": "Record not found"},
                },
            },
            "delete": {
                "tags": [tag],
                "summary": f"Delete {tag} record",
                "parameters": [item_id_parameter()],
                "responses": {
                    "204": {"description": "Record deleted"},
                    "404": {"description": "Record not found"},
                },
            },
        },
    }


def item_id_parameter() -> dict[str, object]:
    return {
        "name": "item_id",
        "in": "path",
        "required": True,
        "schema": {"type": "integer"},
    }
