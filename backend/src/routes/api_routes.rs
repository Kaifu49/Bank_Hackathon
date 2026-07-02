use axum::{
    routing::{get, post},
    Router,
};

use crate::handlers::{
    docs_handler::{openapi, swagger_ui},
    entity_handler::{get_entity, get_entity_aliases, list_entities},
    investigation_handler::{
        clusters, counterparties, entity_explanation, entity_risk_profile, money_flow,
        money_trail, round_trip_explanation, round_trips, timeline, top_risks,
        top_suspicious,
    },
    job_handler::get_job_status,
    report_handler::{case_summary, report_docx, report_excel, report_json, report_pdf},
    statement_handler::{
        clear_database, delete_statement, get_statement, get_transactions,
        get_validation_report, list_statements, upload_statement,
    },
};
use crate::state::app_state::AppState;

pub fn api_routes() -> Router<AppState> {
    Router::new()
        // ---- ingestion ----
        .route("/api/v1/statements/upload", post(upload_statement))
        .route("/api/v1/statements", get(list_statements))
        .route("/api/v1/statements/{id}", get(get_statement).delete(delete_statement))
        .route("/api/v1/database/clear", post(clear_database))
        .route("/api/v1/statements/{id}/transactions", get(get_transactions))
        .route("/api/v1/statements/{id}/validation-report", get(get_validation_report))
        // ---- jobs ----
        .route("/api/v1/jobs/{job_id}/status", get(get_job_status))
        // legacy alias (param named {id} to satisfy matchit consistency)
        .route("/api/v1/statements/{id}/status", get(get_job_status))
        // ---- entities ----
        .route("/api/v1/entities", get(list_entities))
        .route("/api/v1/entities/{id}", get(get_entity))
        .route("/api/v1/entities/{id}/aliases", get(get_entity_aliases))
        .route("/api/v1/entities/{id}/risk-profile", get(entity_risk_profile))
        .route("/api/v1/entities/{id}/explanation", get(entity_explanation))
        // ---- investigations ----
        .route("/api/v1/investigations/{case_id}/round-trips", get(round_trips))
        .route(
            "/api/v1/investigations/{case_id}/round-trips/{chain_id}/explanation",
            get(round_trip_explanation),
        )
        .route("/api/v1/investigations/{case_id}/money-flow", get(money_flow))
        .route("/api/v1/investigations/{case_id}/graph/clusters", get(clusters))
        .route(
            "/api/v1/investigations/{case_id}/money-trail/{transaction_id}",
            get(money_trail),
        )
        .route("/api/v1/investigations/{case_id}/timeline", get(timeline))
        .route(
            "/api/v1/investigations/{case_id}/top-suspicious-accounts",
            get(top_suspicious),
        )
        .route("/api/v1/investigations/{case_id}/top-risks", get(top_risks))
        .route("/api/v1/investigations/{case_id}/counterparties", get(counterparties))
        // ---- cases + reports ----
        .route("/api/v1/cases/{case_id}/summary", get(case_summary))
        .route("/api/v1/reports/{case_id}/json", get(report_json))
        .route("/api/v1/reports/{case_id}/pdf", get(report_pdf))
        .route("/api/v1/reports/{case_id}/excel", get(report_excel))
        .route("/api/v1/reports/{case_id}/docx", get(report_docx))
        // ---- docs ----
        .route("/openapi.json", get(openapi))
        .route("/docs", get(swagger_ui))
}
