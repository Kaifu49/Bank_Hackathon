use axum::Json;
use serde_json::{json, Value};

use crate::config::services::SERVICES;
use crate::services::service_checker::check_service;

pub async fn health() -> Json<Value> {
    Json(json!({
        "status": "healthy",
        "service": "finintel-backend"
    }))
}

pub async fn test_ocr() -> Json<Value> {
    match reqwest::get(
        format!("{}/health", SERVICES.ocr)
    )
    .await
    {
        Ok(response) => {
            let body: Value =
                response.json().await.unwrap();

            Json(json!({
                "backend_status":"success",
                "ocr_response": body
            }))
        }

        Err(err) => {
            Json(json!({
                "backend_status":"error",
                "message": err.to_string()
            }))
        }
    }
}

pub async fn services_health() -> Json<Value> {

    let (
        ocr,
        standardize,
        entity,
        anomaly,
        temporal,
        graph_ml,
        explainer,
    ) = tokio::join!(
        check_service(SERVICES.ocr),
        check_service(SERVICES.standardize),
        check_service(SERVICES.entity),
        check_service(SERVICES.anomaly),
        check_service(SERVICES.temporal),
        check_service(SERVICES.graph_ml),
        check_service(SERVICES.explainer),
    );

    let all_healthy = [
        &ocr,
        &standardize,
        &entity,
        &anomaly,
        &temporal,
        &graph_ml,
        &explainer,
    ]
    .iter()
    .all(|s| s["status"] == "healthy");

    Json(json!({
        "system_status":
            if all_healthy {
                "healthy"
            } else {
                "degraded"
            },

        "backend": {
            "service":"finintel-backend",
            "status":"healthy"
        },

        "services": {
            "ocr": ocr,
            "standardize": standardize,
            "entity": entity,
            "anomaly": anomaly,
            "temporal": temporal,
            "graph_ml": graph_ml,
            "explainer": explainer
        }
    }))
}