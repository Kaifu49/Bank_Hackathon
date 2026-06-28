use sqlx::{
    PgPool,
};
use uuid::Uuid;
use chrono::NaiveDate;
use crate::models::transaction::Transaction;

pub async fn insert_transaction(

    pool: &PgPool,

    statement_id: Uuid,

    txn: &Transaction,

    raw_row: serde_json::Value,

) -> Result<(), sqlx::Error> {

    sqlx::query(
        r#"
        INSERT INTO transactions (

    id,
    statement_id,

    date,

    sender_account,
    receiver_account,

    amount,

    txn_type,

    upi_id,

    narration,
    narration_normalized,

    balance,

    bank_name,

    reference_number,
    debit_credit,
    platform,

    is_duplicate,
    is_failed,
    is_valid,

    confidence_score,
    validation_notes,

    raw_row
)

        VALUES (

            $1,$2,$3,$4,$5,$6,
            $7,$8,$9,$10,$11,
            $12,$13,
            $14,$15,$16,$17,$18,
            $19, $20, $21

        )
        "#
    )
    .bind(Uuid::new_v4())
    .bind(statement_id)

    .bind(
    txn.date
        .as_ref()
        .and_then(|d| {
            NaiveDate::parse_from_str(
                d,
                "%Y-%m-%d"
            )
            .ok()
        })
)

    .bind(
    &txn.sender_account
)

.bind(
    &txn.receiver_account
)

    .bind(txn.amount)

    .bind(&txn.txn_type)

    .bind(&txn.upi_id)

    .bind(&txn.narration)

    .bind(
        &txn.narration_normalized
    )

    .bind(txn.balance)

    .bind(
    &txn.bank_name
)

    .bind(
        &txn.reference_number
    )

    .bind(
        &txn.debit_credit
    )

    .bind(
        &txn.platform
    )

    .bind(txn.is_duplicate)

    .bind(txn.is_failed)

    .bind(txn.is_valid)

    .bind(txn.confidence_score)

    .bind(
        serde_json::json!(
            txn.validation_notes
        )
    )

    .bind(raw_row)

    .execute(pool)
    .await?;

    Ok(())
}