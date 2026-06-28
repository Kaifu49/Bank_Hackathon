//! Read-side queries for the API (lists, details, reports, summary).
//!
//! NUMERIC columns are cast to ::float8 and JSONB/date/timestamp columns to
//! ::text in SQL, so rows decode with only the sqlx features already enabled
//! (no decimal/json feature needed). JSON text is re-parsed in Rust.

use serde_json::{json, Value};
use sqlx::{PgPool, Row};

use crate::api::AppError;

fn parse_json_text(s: Option<String>) -> Value {
    match s {
        Some(t) => serde_json::from_str(&t).unwrap_or(Value::Null),
        None => Value::Null,
    }
}

// ----- statements --------------------------------------------------------

pub async fn count_statements(db: &PgPool) -> Result<i64, AppError> {
    let row = sqlx::query("SELECT COUNT(*) AS c FROM statements")
        .fetch_one(db)
        .await?;
    Ok(row.get::<i64, _>("c"))
}

pub async fn list_statements(
    db: &PgPool,
    limit: i64,
    offset: i64,
) -> Result<Vec<Value>, AppError> {
    let rows = sqlx::query(
        r#"
        SELECT id::text AS id, filename, bank_name, status,
               upload_time::text AS upload_time,
               account_number, account_holder, ifsc_code,
               opening_balance::float8 AS opening_balance,
               closing_balance::float8 AS closing_balance,
               statement_start_date::text AS statement_start_date,
               statement_end_date::text AS statement_end_date
        FROM statements
        ORDER BY upload_time DESC NULLS LAST
        LIMIT $1 OFFSET $2
        "#,
    )
    .bind(limit)
    .bind(offset)
    .fetch_all(db)
    .await?;

    Ok(rows.iter().map(statement_row_to_json).collect())
}

pub async fn get_statement(db: &PgPool, id: &str) -> Result<Value, AppError> {
    let row = sqlx::query(
        r#"
        SELECT id::text AS id, filename, bank_name, status,
               upload_time::text AS upload_time,
               account_number, account_holder, ifsc_code,
               opening_balance::float8 AS opening_balance,
               closing_balance::float8 AS closing_balance,
               statement_start_date::text AS statement_start_date,
               statement_end_date::text AS statement_end_date
        FROM statements WHERE id = $1::uuid
        "#,
    )
    .bind(id)
    .fetch_optional(db)
    .await?
    .ok_or_else(|| AppError::NotFound(format!("statement {} not found", id)))?;

    Ok(statement_row_to_json(&row))
}

fn statement_row_to_json(row: &sqlx::postgres::PgRow) -> Value {
    json!({
        "id": row.get::<String, _>("id"),
        "filename": row.get::<Option<String>, _>("filename"),
        "bank_name": row.get::<Option<String>, _>("bank_name"),
        "status": row.get::<Option<String>, _>("status"),
        "upload_time": row.get::<Option<String>, _>("upload_time"),
        "account_number": row.get::<Option<String>, _>("account_number"),
        "account_holder": row.get::<Option<String>, _>("account_holder"),
        "ifsc_code": row.get::<Option<String>, _>("ifsc_code"),
        "opening_balance": row.get::<Option<f64>, _>("opening_balance"),
        "closing_balance": row.get::<Option<f64>, _>("closing_balance"),
        "statement_start_date": row.get::<Option<String>, _>("statement_start_date"),
        "statement_end_date": row.get::<Option<String>, _>("statement_end_date"),
    })
}

// ----- transactions ------------------------------------------------------

pub async fn count_transactions(db: &PgPool, statement_id: &str) -> Result<i64, AppError> {
    let row = sqlx::query("SELECT COUNT(*) AS c FROM transactions WHERE statement_id = $1::uuid")
        .bind(statement_id)
        .fetch_one(db)
        .await?;
    Ok(row.get::<i64, _>("c"))
}

pub async fn list_transactions(
    db: &PgPool,
    statement_id: &str,
    limit: i64,
    offset: i64,
) -> Result<Vec<Value>, AppError> {
    let rows = sqlx::query(
        r#"
        SELECT id::text AS id, date::text AS date,
               sender_account, receiver_account,
               amount::float8 AS amount, txn_type, upi_id,
               narration, narration_normalized,
               balance::float8 AS balance, bank_name,
               reference_number, debit_credit, platform,
               is_duplicate, is_failed, is_valid,
               confidence_score,
               validation_notes::text AS validation_notes
        FROM transactions
        WHERE statement_id = $1::uuid
        ORDER BY date NULLS LAST, created_at
        LIMIT $2 OFFSET $3
        "#,
    )
    .bind(statement_id)
    .bind(limit)
    .bind(offset)
    .fetch_all(db)
    .await?;

    Ok(rows.iter().map(txn_row_to_json).collect())
}

fn txn_row_to_json(row: &sqlx::postgres::PgRow) -> Value {
    json!({
        "id": row.get::<String, _>("id"),
        "date": row.get::<Option<String>, _>("date"),
        "sender_account": row.get::<Option<String>, _>("sender_account"),
        "receiver_account": row.get::<Option<String>, _>("receiver_account"),
        "amount": row.get::<Option<f64>, _>("amount"),
        "txn_type": row.get::<Option<String>, _>("txn_type"),
        "upi_id": row.get::<Option<String>, _>("upi_id"),
        "narration": row.get::<Option<String>, _>("narration"),
        "narration_normalized": row.get::<Option<String>, _>("narration_normalized"),
        "balance": row.get::<Option<f64>, _>("balance"),
        "bank_name": row.get::<Option<String>, _>("bank_name"),
        "reference_number": row.get::<Option<String>, _>("reference_number"),
        "debit_credit": row.get::<Option<String>, _>("debit_credit"),
        "platform": row.get::<Option<String>, _>("platform"),
        "is_duplicate": row.get::<Option<bool>, _>("is_duplicate"),
        "is_failed": row.get::<Option<bool>, _>("is_failed"),
        "is_valid": row.get::<Option<bool>, _>("is_valid"),
        "confidence_score": row.get::<Option<f64>, _>("confidence_score"),
        "validation_notes": parse_json_text(row.get::<Option<String>, _>("validation_notes")),
    })
}

// ----- validation report -------------------------------------------------

pub async fn validation_report(db: &PgPool, statement_id: &str) -> Result<Value, AppError> {
    let row = sqlx::query(
        r#"
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE is_duplicate) AS duplicates,
            COUNT(*) FILTER (WHERE is_failed) AS failed,
            COUNT(*) FILTER (WHERE NOT is_valid) AS invalid,
            AVG(confidence_score)::float8 AS avg_confidence
        FROM transactions WHERE statement_id = $1::uuid
        "#,
    )
    .bind(statement_id)
    .fetch_one(db)
    .await?;

    let issues = sqlx::query(
        r#"
        SELECT id::text AS id, date::text AS date,
               amount::float8 AS amount, debit_credit, narration,
               is_duplicate, is_failed, is_valid,
               validation_notes::text AS validation_notes
        FROM transactions
        WHERE statement_id = $1::uuid
          AND (is_duplicate OR is_failed OR NOT is_valid)
        ORDER BY date NULLS LAST
        LIMIT 100
        "#,
    )
    .bind(statement_id)
    .fetch_all(db)
    .await?;

    let issue_list: Vec<Value> = issues
        .iter()
        .map(|r| {
            json!({
                "id": r.get::<String, _>("id"),
                "date": r.get::<Option<String>, _>("date"),
                "amount": r.get::<Option<f64>, _>("amount"),
                "debit_credit": r.get::<Option<String>, _>("debit_credit"),
                "narration": r.get::<Option<String>, _>("narration"),
                "is_duplicate": r.get::<Option<bool>, _>("is_duplicate"),
                "is_failed": r.get::<Option<bool>, _>("is_failed"),
                "is_valid": r.get::<Option<bool>, _>("is_valid"),
                "validation_notes": parse_json_text(r.get::<Option<String>, _>("validation_notes")),
            })
        })
        .collect();

    Ok(json!({
        "statement_id": statement_id,
        "summary": {
            "total": row.get::<i64, _>("total"),
            "duplicates": row.get::<i64, _>("duplicates"),
            "failed_or_reversed": row.get::<i64, _>("failed"),
            "invalid": row.get::<i64, _>("invalid"),
            "average_confidence": row.get::<Option<f64>, _>("avg_confidence"),
        },
        "issues": issue_list,
    }))
}

// ----- entities ----------------------------------------------------------

pub async fn count_entities(db: &PgPool, etype: &Option<String>) -> Result<i64, AppError> {
    let row = match etype {
        Some(t) => {
            sqlx::query("SELECT COUNT(*) AS c FROM entities WHERE entity_type = $1")
                .bind(t)
                .fetch_one(db)
                .await?
        }
        None => sqlx::query("SELECT COUNT(*) AS c FROM entities").fetch_one(db).await?,
    };
    Ok(row.get::<i64, _>("c"))
}

pub async fn list_entities(
    db: &PgPool,
    etype: &Option<String>,
    limit: i64,
    offset: i64,
) -> Result<Vec<Value>, AppError> {
    let rows = match etype {
        Some(t) => {
            sqlx::query(
                r#"SELECT id::text AS id, entity_type, identifier, display_name,
                          metadata::text AS metadata
                   FROM entities WHERE entity_type = $1
                   ORDER BY identifier LIMIT $2 OFFSET $3"#,
            )
            .bind(t)
            .bind(limit)
            .bind(offset)
            .fetch_all(db)
            .await?
        }
        None => {
            sqlx::query(
                r#"SELECT id::text AS id, entity_type, identifier, display_name,
                          metadata::text AS metadata
                   FROM entities ORDER BY identifier LIMIT $1 OFFSET $2"#,
            )
            .bind(limit)
            .bind(offset)
            .fetch_all(db)
            .await?
        }
    };
    Ok(rows.iter().map(entity_row_to_json).collect())
}

pub async fn get_entity(db: &PgPool, id: &str) -> Result<Value, AppError> {
    let row = sqlx::query(
        r#"SELECT id::text AS id, entity_type, identifier, display_name,
                  metadata::text AS metadata
           FROM entities WHERE id = $1::uuid"#,
    )
    .bind(id)
    .fetch_optional(db)
    .await?
    .ok_or_else(|| AppError::NotFound(format!("entity {} not found", id)))?;
    Ok(entity_row_to_json(&row))
}

fn entity_row_to_json(row: &sqlx::postgres::PgRow) -> Value {
    json!({
        "id": row.get::<String, _>("id"),
        "entity_type": row.get::<Option<String>, _>("entity_type"),
        "identifier": row.get::<Option<String>, _>("identifier"),
        "display_name": row.get::<Option<String>, _>("display_name"),
        "metadata": parse_json_text(row.get::<Option<String>, _>("metadata")),
    })
}

// ----- case summary ------------------------------------------------------

pub async fn case_summary(db: &PgPool) -> Result<Value, AppError> {
    let row = sqlx::query(
        r#"
        SELECT
            (SELECT COUNT(*) FROM statements)   AS statements,
            (SELECT COUNT(*) FROM transactions) AS transactions,
            (SELECT COUNT(*) FROM entities)     AS entities,
            (SELECT COUNT(*) FROM transactions WHERE is_duplicate) AS duplicates,
            (SELECT COUNT(*) FROM transactions WHERE is_failed)    AS failed,
            (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                WHERE debit_credit = 'CREDIT') AS total_credit,
            (SELECT COALESCE(SUM(amount),0)::float8 FROM transactions
                WHERE debit_credit = 'DEBIT')  AS total_debit
        "#,
    )
    .fetch_one(db)
    .await?;

    Ok(json!({
        "statements": row.get::<i64, _>("statements"),
        "transactions": row.get::<i64, _>("transactions"),
        "entities": row.get::<i64, _>("entities"),
        "duplicates": row.get::<i64, _>("duplicates"),
        "failed_or_reversed": row.get::<i64, _>("failed"),
        "total_credit": row.get::<f64, _>("total_credit"),
        "total_debit": row.get::<f64, _>("total_debit"),
    }))
}
