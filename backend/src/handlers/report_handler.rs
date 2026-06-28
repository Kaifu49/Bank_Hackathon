use axum::extract::{Path, State};
use serde_json::{json, Value};

use crate::{
    api::{ApiResponse, ApiResult, AppError},
    repositories::read_repository,
    services::proxy::get_json,
    state::app_state::AppState,
};

/// GET /api/v1/cases/{case_id}/summary  — dashboard payload
pub async fn case_summary(
    State(state): State<AppState>,
    Path(_case_id): Path<String>,
) -> ApiResult<Value> {
    let mut summary = read_repository::case_summary(&state.db).await?;

    // best-effort enrichment from the graph service
    let g = &state.services.graph;
    if let Ok(top) = get_json(&state.http_client, &format!("{}/risk/top?limit=5", g)).await {
        if let Value::Object(ref mut m) = summary {
            m.insert("top_risks".into(),
                     top.get("top_risks").cloned().unwrap_or(json!([])));
        }
    }
    if let Ok(mf) = get_json(&state.http_client, &format!("{}/flow/money-flow/all", g)).await {
        if let Value::Object(ref mut m) = summary {
            m.insert("money_flow_summary".into(),
                     mf.get("summary").cloned().unwrap_or(Value::Null));
        }
    }
    Ok(ApiResponse::success(summary))
}

/// GET /api/v1/reports/{case_id}/json  — machine-readable investigation report
pub async fn report_json(
    State(state): State<AppState>,
    Path(_case_id): Path<String>,
) -> ApiResult<Value> {
    let g = &state.services.graph;
    let summary = read_repository::case_summary(&state.db).await?;
    let analysis = get_json(&state.http_client, &format!("{}/flow/analyze/all", g))
        .await
        .unwrap_or(Value::Null);

    Ok(ApiResponse::success(json!({
        "report_type": "investigation",
        "generated_at": chrono::Utc::now().to_rfc3339(),
        "case_summary": summary,
        "money_flow": analysis.get("summary").cloned().unwrap_or(Value::Null),
        "round_trips": analysis.get("round_trips").cloned().unwrap_or(json!([])),
        "communities": analysis.get("communities").cloned().unwrap_or(json!([])),
        "top_risks": {
            "note": "see /api/v1/investigations/all/top-risks"
        }
    })))
}

/// GET /api/v1/reports/{case_id}/pdf  — Phase 7
pub async fn report_pdf(
    State(_state): State<AppState>,
    Path(_case_id): Path<String>,
) -> ApiResult<Value> {
    Err(AppError::NotImplemented(
        "PDF export is delivered in Phase 7 (Reporting). Use /reports/{case_id}/json for now."
            .into(),
    ))
}

/// GET /api/v1/reports/{case_id}/excel  — Phase 7
pub async fn report_excel(
    State(_state): State<AppState>,
    Path(_case_id): Path<String>,
) -> ApiResult<Value> {
    Err(AppError::NotImplemented(
        "Excel export is delivered in Phase 7 (Reporting). Use /reports/{case_id}/json for now."
            .into(),
    ))
}
