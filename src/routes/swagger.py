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
        <style>
          body {
            margin: 0;
            background: #001f1d;
          }

          .swagger-ui {
            color: #e9fff8;
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }

          .swagger-ui .info .title,
          .swagger-ui .opblock-tag,
          .swagger-ui .opblock .opblock-summary-path,
          .swagger-ui .opblock .opblock-summary-description,
          .swagger-ui .opblock-description-wrapper p,
          .swagger-ui .response-col_status,
          .swagger-ui table thead tr td,
          .swagger-ui table thead tr th,
          .swagger-ui .parameter__name,
          .swagger-ui .parameter__type,
          .swagger-ui .tab li,
          .swagger-ui label,
          .swagger-ui p,
          .swagger-ui h1,
          .swagger-ui h2,
          .swagger-ui h3,
          .swagger-ui h4,
          .swagger-ui h5 {
            color: #e9fff8;
          }

          .swagger-ui .info {
            margin: 48px 0 38px;
          }

          .swagger-ui .info .title {
            font-size: 46px;
            font-weight: 800;
          }

          .swagger-ui .info a {
            color: #33d6ff;
          }

          .swagger-ui .scheme-container,
          .swagger-ui section.models,
          .swagger-ui .opblock,
          .swagger-ui .opblock-body {
            background: #071920;
            border-color: #00a8b8;
            box-shadow: none;
          }

          .swagger-ui .opblock-tag {
            border-bottom-color: rgba(0, 168, 184, 0.35);
            font-size: 30px;
            font-weight: 800;
          }

          .swagger-ui .opblock .opblock-summary {
            border-color: rgba(0, 168, 184, 0.35);
          }

          .swagger-ui .opblock.opblock-get {
            background: rgba(0, 112, 140, 0.26);
            border-color: #4eb8ff;
          }

          .swagger-ui .opblock.opblock-post {
            background: rgba(0, 139, 104, 0.24);
            border-color: #42d69f;
          }

          .swagger-ui .opblock.opblock-patch {
            background: rgba(0, 139, 104, 0.24);
            border-color: #47e0c1;
          }

          .swagger-ui .opblock.opblock-delete {
            background: rgba(92, 12, 18, 0.36);
            border-color: #ff4d57;
          }

          .swagger-ui .opblock .opblock-summary-method {
            color: #ffffff;
            text-shadow: none;
          }

          .swagger-ui .opblock .opblock-summary-path {
            font-weight: 800;
          }

          .swagger-ui .opblock .opblock-summary-description,
          .swagger-ui .markdown code,
          .swagger-ui .parameter__in,
          .swagger-ui .prop-type,
          .swagger-ui .model-title,
          .swagger-ui .model {
            color: #b7d7d4;
          }

          .swagger-ui input,
          .swagger-ui textarea,
          .swagger-ui select {
            background: #061116;
            border-color: #00a8b8;
            color: #f5fffb;
          }

          .swagger-ui .btn {
            border-color: #00e0c6;
            color: #e9fff8;
          }

          .swagger-ui .btn.execute {
            background: #d9ffe3;
            border-color: #d9ffe3;
            color: #061116;
          }

          .swagger-ui .responses-inner h4,
          .swagger-ui .responses-inner h5,
          .swagger-ui .response-col_links,
          .swagger-ui .response-col_description {
            color: #e9fff8;
          }

          .swagger-ui .highlight-code,
          .swagger-ui .microlight {
            background: #020b0f;
            color: #f5fffb;
          }
        </style>
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
