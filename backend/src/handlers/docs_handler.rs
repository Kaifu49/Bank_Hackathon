//! OpenAPI spec (built in code from the route table) + Swagger UI at /docs.
//! Kept in code (not a hand-edited file) so it stays close to the routes; the
//! UI is loaded from the public Swagger CDN so no asset bundling is needed.

use axum::{response::Html, Json};
use serde_json::{json, Value};

// (method, path, tag, summary)
const ENDPOINTS: &[(&str, &str, &str, &str)] = &[
    ("get", "/health", "system", "Backend health"),
    ("get", "/services/health", "system", "Health of all ML services"),
    ("post", "/api/v1/statements/upload", "ingestion",
        "Upload a statement (multipart: file, optional bank_name)"),
    ("get", "/api/v1/jobs/{job_id}/status", "ingestion", "Poll processing job status"),
    ("get", "/api/v1/statements", "ingestion", "List statements (paginated)"),
    ("get", "/api/v1/statements/{id}", "ingestion", "Statement metadata"),
    ("get", "/api/v1/statements/{id}/transactions", "ingestion",
        "Standardized + cleaned transactions (paginated)"),
    ("get", "/api/v1/statements/{id}/validation-report", "validation",
        "Duplicates / failed / balance mismatches"),
    ("get", "/api/v1/entities", "entities", "List canonical entities (paginated, ?type=)"),
    ("get", "/api/v1/entities/{id}", "entities", "Entity detail"),
    ("get", "/api/v1/entities/{id}/aliases", "entities", "Entity aliases"),
    ("get", "/api/v1/entities/{id}/risk-profile", "risk", "Fused risk profile for an entity"),
    ("get", "/api/v1/entities/{id}/explanation", "explainability",
        "Why an entity is risky (factors + evidence)"),
    ("get", "/api/v1/investigations/{case_id}/round-trips", "investigation",
        "Circular / round-trip chains"),
    ("get", "/api/v1/investigations/{case_id}/round-trips/{chain_id}/explanation",
        "explainability", "Explain a specific round-trip chain"),
    ("get", "/api/v1/investigations/{case_id}/money-flow", "investigation",
        "Money-flow graph (nodes + edges + summary)"),
    ("get", "/api/v1/investigations/{case_id}/graph/clusters", "investigation",
        "Network communities"),
    ("get", "/api/v1/investigations/{case_id}/money-trail/{transaction_id}", "investigation",
        "FIFO money-trail for a credit transaction"),
    ("get", "/api/v1/investigations/{case_id}/timeline", "investigation",
        "Chronological events (?account=)"),
    ("get", "/api/v1/investigations/{case_id}/top-suspicious-accounts", "investigation",
        "Ranked suspicious accounts (?limit=)"),
    ("get", "/api/v1/investigations/{case_id}/top-risks", "risk", "Top fused risks (?limit=)"),
    ("get", "/api/v1/investigations/{case_id}/counterparties", "investigation",
        "Counterparty breakdown (?account=)"),
    ("get", "/api/v1/cases/{case_id}/summary", "reporting", "Dashboard summary payload"),
    ("get", "/api/v1/reports/{case_id}/json", "reporting", "Investigation report (JSON)"),
    ("get", "/api/v1/reports/{case_id}/pdf", "reporting", "Investigation report (PDF) — Phase 7"),
    ("get", "/api/v1/reports/{case_id}/excel", "reporting", "Investigation report (Excel) — Phase 7"),
];

fn path_params(path: &str) -> Vec<Value> {
    let mut params = vec![];
    for part in path.split('/') {
        if part.starts_with('{') && part.ends_with('}') {
            let name = &part[1..part.len() - 1];
            params.push(json!({
                "name": name,
                "in": "path",
                "required": true,
                "schema": { "type": "string" }
            }));
        }
    }
    params
}

pub async fn openapi() -> Json<Value> {
    let mut paths = serde_json::Map::new();

    for (method, path, tag, summary) in ENDPOINTS {
        let op = json!({
            "tags": [tag],
            "summary": summary,
            "parameters": path_params(path),
            "responses": {
                "200": {
                    "description": "Standard success envelope",
                    "content": { "application/json": {
                        "schema": { "$ref": "#/components/schemas/ApiResponse" }
                    }}
                },
                "default": {
                    "description": "Standard error envelope",
                    "content": { "application/json": {
                        "schema": { "$ref": "#/components/schemas/ApiError" }
                    }}
                }
            }
        });

        let entry = paths
            .entry(path.to_string())
            .or_insert_with(|| json!({}));
        if let Value::Object(m) = entry {
            m.insert(method.to_string(), op);
        }
    }

    let spec = json!({
        "openapi": "3.0.3",
        "info": {
            "title": "FinIntel API",
            "version": "1.0.0",
            "description": "AI-Powered Financial Crime Investigation Platform — backend API. \
All endpoints return the standard envelope { success, data, error, meta }."
        },
        "servers": [{ "url": "/" }],
        "paths": Value::Object(paths),
        "components": {
            "schemas": {
                "ApiResponse": {
                    "type": "object",
                    "properties": {
                        "success": { "type": "boolean", "example": true },
                        "data": {},
                        "error": { "nullable": true },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "request_id": { "type": "string", "format": "uuid" },
                                "timestamp": { "type": "string", "format": "date-time" },
                                "pagination": {
                                    "type": "object",
                                    "nullable": true,
                                    "properties": {
                                        "page": { "type": "integer" },
                                        "page_size": { "type": "integer" },
                                        "total_items": { "type": "integer" },
                                        "total_pages": { "type": "integer" }
                                    }
                                }
                            }
                        }
                    }
                },
                "ApiError": {
                    "type": "object",
                    "properties": {
                        "success": { "type": "boolean", "example": false },
                        "data": { "nullable": true },
                        "error": {
                            "type": "object",
                            "properties": {
                                "code": { "type": "string", "example": "VALIDATION_ERROR" },
                                "message": { "type": "string" },
                                "details": { "type": "object" }
                            }
                        },
                        "meta": { "type": "object" }
                    }
                }
            }
        }
    });

    Json(spec)
}

pub async fn swagger_ui() -> Html<&'static str> {
    Html(
        r#"<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FinIntel API — Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
      url: '/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true
    });
  </script>
</body>
</html>"#,
    )
}
