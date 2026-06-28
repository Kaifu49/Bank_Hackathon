use axum::extract::{Path, State};
use serde_json::Value;
use uuid::Uuid;

use crate::{
    api::{ApiResponse, ApiResult},
    repositories::job_repository::get_job,
    state::app_state::AppState,
};

/// GET /api/v1/jobs/{job_id}/status
/// (also aliased at /api/v1/statements/{job_id}/status for backward compat)
pub async fn get_job_status(
    State(state): State<AppState>,
    Path(job_id): Path<Uuid>,
) -> ApiResult<Value> {
    let job = get_job(&state.db, job_id).await?;
    Ok(ApiResponse::success(job))
}
