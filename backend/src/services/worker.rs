//! Background worker: runs the ingestion pipeline per uploaded statement and
//! keeps the DB-backed job row up to date (queued -> processing -> completed |
//! failed) so the status endpoint reflects reality.

use reqwest::Client;
use serde_json::{json, Value};
use sqlx::PgPool;
use tokio::sync::mpsc::Receiver;

use crate::{
    models::{
        entity::CanonicalEntity,
        statement::ProcessingJob,
        transaction::Transaction,
    },
    repositories::{job_repository::update_job, statement::update_statement_status},
    services::{entity_service::save_entities, transaction_service::save_transactions},
};

// service URLs (kept local to the pipeline; the API gateway uses ServiceConfig)
const OCR: &str = "http://localhost:8001/extract";
const STANDARDIZE: &str = "http://localhost:8002/standardize";
const VALIDATE: &str = "http://localhost:8004/validate";
const ENTITY: &str = "http://localhost:8003/resolve";
const GRAPH_ANALYZE: &str = "http://localhost:8005/flow/analyze/all";

pub async fn start_worker(mut receiver: Receiver<ProcessingJob>, db: PgPool) {
    let client = Client::new();

    while let Some(job) = receiver.recv().await {
        println!("\nProcessing statement: {}", job.statement_id);

        match process_job(&client, &db, &job).await {
            Ok(()) => {
                update_job(&db, job.job_id, "completed", 100, "done", None).await;
                let _ = update_statement_status(&db, job.statement_id, "completed").await;
                println!("Job {} completed", job.job_id);
            }
            Err(err) => {
                update_job(&db, job.job_id, "failed", 0, "error", Some(&err)).await;
                let _ = update_statement_status(&db, job.statement_id, "failed").await;
                println!("Job {} FAILED: {}", job.job_id, err);
            }
        }
    }
}

async fn process_job(
    client: &Client,
    db: &PgPool,
    job: &ProcessingJob,
) -> Result<(), String> {
    update_job(db, job.job_id, "processing", 10, "ocr", None).await;
    let _ = update_statement_status(db, job.statement_id, "processing").await;

    let abs_path = std::fs::canonicalize(&job.file_path)
        .map_err(|e| format!("path error: {}", e))?
        .to_string_lossy()
        .to_string();

    // 1. OCR / extraction
    let ocr = post(client, OCR, &json!({ "file_path": abs_path })).await?;

    // 2. standardize
    update_job(db, job.job_id, "processing", 30, "standardize", None).await;
    let standardized =
        post(client, STANDARDIZE, &json!({ "rows": ocr["rows"] })).await?;

    // 3. validate
    update_job(db, job.job_id, "processing", 45, "validate", None).await;
    let validated = post(
        client,
        VALIDATE,
        &json!({ "transactions": standardized["transactions"] }),
    )
    .await?;

    // 4. persist transactions
    let txns: Vec<Transaction> =
        serde_json::from_value(validated["transactions"].clone()).unwrap_or_default();
    println!("Saving {} transactions", txns.len());
    save_transactions(db, job.statement_id, txns).await;

    // 5. entities
    update_job(db, job.job_id, "processing", 65, "entities", None).await;
    let entity_resp = post(
        client,
        ENTITY,
        &json!({ "transactions": validated["transactions"] }),
    )
    .await?;
    let entities: Vec<CanonicalEntity> =
        serde_json::from_value(entity_resp["canonical_entities"].clone()).unwrap_or_default();
    save_entities(db, entities).await;

    // 6. graph intelligence (DB-driven, whole network) — best-effort
    update_job(db, job.job_id, "processing", 85, "graph", None).await;
    match get(client, GRAPH_ANALYZE).await {
        Ok(g) => {
            let trips = g["round_trips"].as_array().map(|a| a.len()).unwrap_or(0);
            println!("Graph intelligence refreshed (round-trips: {})", trips);
        }
        Err(e) => println!("Graph trigger failed (non-fatal): {}", e),
    }

    Ok(())
}

async fn post(client: &Client, url: &str, body: &Value) -> Result<Value, String> {
    let resp = client
        .post(url)
        .json(body)
        .send()
        .await
        .map_err(|e| format!("{} request error: {}", url, e))?;
    if !resp.status().is_success() {
        return Err(format!("{} returned {}", url, resp.status()));
    }
    resp.json::<Value>()
        .await
        .map_err(|e| format!("{} bad JSON: {}", url, e))
}

async fn get(client: &Client, url: &str) -> Result<Value, String> {
    let resp = client
        .get(url)
        .send()
        .await
        .map_err(|e| format!("{} request error: {}", url, e))?;
    if !resp.status().is_success() {
        return Err(format!("{} returned {}", url, resp.status()));
    }
    resp.json::<Value>()
        .await
        .map_err(|e| format!("{} bad JSON: {}", url, e))
}
