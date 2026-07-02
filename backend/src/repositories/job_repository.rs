use serde_json::{json, Value};
use sqlx::{PgPool, Row};
use uuid::Uuid;

use crate::api::AppError;

pub async fn insert_job(
    db: &PgPool,
    job_id: Uuid,
    statement_id: Uuid,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO jobs (id, statement_id, status, progress, stage)
        VALUES ($1, $2, 'queued', 0, 'queued')
        "#,
    )
    .bind(job_id)
    .bind(statement_id)
    .execute(db)
    .await?;
    Ok(())
}

pub async fn update_job(
    db: &PgPool,
    job_id: Uuid,
    status: &str,
    progress: i32,
    stage: &str,
    error: Option<&str>,
) {
    let _ = sqlx::query(
        r#"
        UPDATE jobs
        SET status = $1, progress = $2, stage = $3, error = $4, updated_at = NOW()
        WHERE id = $5
        "#,
    )
    .bind(status)
    .bind(progress)
    .bind(stage)
    .bind(error)
    .bind(job_id)
    .execute(db)
    .await;
}

pub async fn get_job(db: &PgPool, job_id: Uuid) -> Result<Value, AppError> {
    let row = sqlx::query(
        r#"
        SELECT id, statement_id, status, progress, stage, error,
               created_at, updated_at
        FROM jobs WHERE id = $1
        "#,
    )
    .bind(job_id)
    .fetch_optional(db)
    .await?;

    let row = row.ok_or_else(|| AppError::NotFound(format!("job {} not found", job_id)))?;

    Ok(json!({
        "job_id": row.get::<Uuid, _>("id"),
        "statement_id": row.get::<Uuid, _>("statement_id"),
        "status": row.get::<String, _>("status"),
        "progress": row.get::<i32, _>("progress"),
        "stage": row.get::<Option<String>, _>("stage"),
        "error": row.get::<Option<String>, _>("error"),
    }))
}
