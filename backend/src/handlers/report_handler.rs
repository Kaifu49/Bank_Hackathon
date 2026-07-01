use axum::{
    body::Body,
    extract::{Path, State},
    http::header,
    response::Response,
};
use serde_json::{json, Value};

use crate::{
    api::{ApiResponse, ApiResult, AppError},
    repositories::read_repository,
    services::proxy::{fetch_bytes, get_json},
    state::app_state::AppState,
};

/// GET /api/v1/cases/{case_id}/summary  — dashboard payload
pub async fn case_summary(
    State(state): State<AppState>,
    Path(_case_id): Path<String>,
) -> ApiResult<Value> {
    let mut summary = read_repository::case_summary(&state.db).await?;

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

/// GET /api/v1/reports/{case_id}/json  — machine-readable report (enveloped)
pub async fn report_json(
    State(state): State<AppState>,
    Path(case_id): Path<String>,
) -> ApiResult<Value> {
    let url = format!("{}/report/{}/json", state.services.report, case_id);
    let data = get_json(&state.http_client, &url).await?;
    Ok(ApiResponse::success(data))
}

async fn download(
    state: &AppState,
    case_id: &str,
    fmt: &str,
) -> Result<Response, AppError> {
    let url = format!("{}/report/{}/{}", state.services.report, case_id, fmt);
    let (content_type, disposition, bytes) = fetch_bytes(&state.http_client, &url).await?;
    let mut builder = Response::builder()
        .status(200)
        .header(header::CONTENT_TYPE, content_type);
    if let Some(d) = disposition {
        builder = builder.header(header::CONTENT_DISPOSITION, d);
    }
    builder
        .body(Body::from(bytes))
        .map_err(|e| AppError::Internal(format!("response build error: {}", e)))
}

/// GET /api/v1/reports/{case_id}/pdf
pub async fn report_pdf(
    State(state): State<AppState>,
    Path(case_id): Path<String>,
) -> Result<Response, AppError> {
    download(&state, &case_id, "pdf").await
}

/// GET /api/v1/reports/{case_id}/excel
pub async fn report_excel(
    State(state): State<AppState>,
    Path(case_id): Path<String>,
) -> Result<Response, AppError> {
    download(&state, &case_id, "excel").await
}

/// GET /api/v1/reports/{case_id}/docx
pub async fn report_docx(
    State(state): State<AppState>,
    Path(case_id): Path<String>,
) -> Result<Response, AppError> {
    download(&state, &case_id, "docx").await
}
