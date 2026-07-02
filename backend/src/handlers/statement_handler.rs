use axum::{
    extract::{Multipart, Path, Query, State},
};
use serde_json::{json, Value};
use uuid::Uuid;

use crate::{
    api::{ApiResponse, ApiResult, AppError, Pagination},
    models::statement::ProcessingJob,
    repositories::{
        job_repository::insert_job,
        read_repository,
        statement::insert_statement,
    },
    services::storage::create_statement_directory,
    state::app_state::AppState,
};

const ALLOWED_EXT: [&str; 9] =
    ["pdf", "csv", "xlsx", "xls", "docx", "txt", "png", "jpg", "jpeg"];

/// POST /api/v1/statements/upload  (multipart: file, optional bank_name)
pub async fn upload_statement(
    State(state): State<AppState>,
    mut multipart: Multipart,
) -> ApiResult<Value> {
    let statement_id = Uuid::new_v4();
    let job_id = Uuid::new_v4();

    let mut bank_name: Option<String> = None;
    let mut filename = String::from("statement");
    let mut saved_path: Option<std::path::PathBuf> = None;

    while let Some(field) = multipart
        .next_field()
        .await
        .map_err(|e| AppError::Validation(format!("invalid multipart: {}", e)))?
    {
        match field.name() {
            Some("bank_name") => {
                bank_name = field
                    .text()
                    .await
                    .map_err(|e| AppError::Validation(format!("bad bank_name: {}", e)))
                    .ok();
            }
            Some("file") => {
                let raw_filename = field
                    .file_name()
                    .unwrap_or("statement")
                    .to_string();

                filename = std::path::Path::new(&raw_filename)
                    .file_name()
                    .map(|f| f.to_string_lossy().to_string())
                    .unwrap_or(raw_filename);

                let ext = std::path::Path::new(&filename)
                    .extension()
                    .and_then(|e| e.to_str())
                    .map(|e| e.to_lowercase())
                    .unwrap_or_default();

                if !ALLOWED_EXT.contains(&ext.as_str()) {
                    return Err(AppError::UnsupportedMediaType(format!(
                        "unsupported file type: '{}'. Allowed: {:?}",
                        ext, ALLOWED_EXT
                    )));
                }

                let bytes = field
                    .bytes()
                    .await
                    .map_err(|e| AppError::Validation(format!("failed to read file: {}", e)))?;

                let dir = create_statement_directory(statement_id)
                    .await
                    .map_err(|e| AppError::Internal(format!("storage error: {}", e)))?;
                let path = dir.join(&filename);
                tokio::fs::write(&path, bytes)
                    .await
                    .map_err(|e| AppError::Internal(format!("failed to save file: {}", e)))?;
                saved_path = Some(path);
            }
            _ => {}
        }
    }

    let file_path = saved_path
        .ok_or_else(|| AppError::Validation("no 'file' field in upload".into()))?;

    insert_statement(
        &state.db,
        statement_id,
        filename.clone(),
        bank_name.clone(),
        file_path.to_string_lossy().to_string(),
    )
    .await
    .map_err(|e| AppError::Internal(format!("db insert failed: {}", e)))?;

    insert_job(&state.db, job_id, statement_id)
        .await
        .map_err(|e| AppError::Internal(format!("job insert failed: {}", e)))?;

    let job = ProcessingJob {
        job_id,
        statement_id,
        file_path: file_path.to_string_lossy().to_string(),
    };
    state
        .job_sender
        .send(job)
        .await
        .map_err(|e| AppError::Internal(format!("failed to enqueue: {}", e)))?;

    Ok(ApiResponse::success(json!({
        "job_id": job_id,
        "statement_id": statement_id,
        "status": "queued"
    })))
}

/// GET /api/v1/statements
pub async fn list_statements(
    State(state): State<AppState>,
    Query(page): Query<Pagination>,
) -> ApiResult<Vec<Value>> {
    let total = read_repository::count_statements(&state.db).await?;
    let items =
        read_repository::list_statements(&state.db, page.page_size(), page.offset()).await?;
    Ok(ApiResponse::success_paginated(items, page.meta(total)))
}

/// GET /api/v1/statements/{id}
pub async fn get_statement(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Value> {
    let s = read_repository::get_statement(&state.db, &id).await?;
    Ok(ApiResponse::success(s))
}

/// GET /api/v1/statements/{id}/transactions
pub async fn get_transactions(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Query(page): Query<Pagination>,
) -> ApiResult<Vec<Value>> {
    let total = read_repository::count_transactions(&state.db, &id).await?;
    let items =
        read_repository::list_transactions(&state.db, &id, page.page_size(), page.offset())
            .await?;
    Ok(ApiResponse::success_paginated(items, page.meta(total)))
}

/// GET /api/v1/statements/{id}/validation-report
pub async fn get_validation_report(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Value> {
    let report = read_repository::validation_report(&state.db, &id).await?;
    Ok(ApiResponse::success(report))
}

/// DELETE /api/v1/statements/{id}
pub async fn delete_statement(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Value> {
    let statement_uuid = Uuid::parse_str(&id)
        .map_err(|e| AppError::Validation(format!("invalid statement uuid: {}", e)))?;
        
    let mut tx = state.db.begin().await
        .map_err(|e| AppError::Internal(format!("failed to start transaction: {}", e)))?;
        
    sqlx::query("DELETE FROM jobs WHERE statement_id = $1")
        .bind(statement_uuid)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::Internal(format!("failed to delete jobs: {}", e)))?;
        
    sqlx::query("DELETE FROM transactions WHERE statement_id = $1")
        .bind(statement_uuid)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::Internal(format!("failed to delete transactions: {}", e)))?;
        
    sqlx::query("DELETE FROM statements WHERE id = $1")
        .bind(statement_uuid)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::Internal(format!("failed to delete statement: {}", e)))?;
        
    tx.commit().await
        .map_err(|e| AppError::Internal(format!("failed to commit transaction: {}", e)))?;
        
    Ok(ApiResponse::success(json!({ "deleted": id })))
}

/// POST /api/v1/database/clear
pub async fn clear_database(State(state): State<AppState>) -> ApiResult<Value> {
    let mut tx = state.db.begin().await
        .map_err(|e| AppError::Internal(format!("failed to start transaction: {}", e)))?;
        
    sqlx::query("TRUNCATE TABLE jobs, risk_profiles, entities, transactions, statements CASCADE;")
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::Internal(format!("failed to truncate tables: {}", e)))?;
        
    tx.commit().await
        .map_err(|e| AppError::Internal(format!("failed to commit transaction: {}", e)))?;
        
    Ok(ApiResponse::success(json!({ "status": "cleared" })))
}
