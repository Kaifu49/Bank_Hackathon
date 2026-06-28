use sqlx::PgPool;
use uuid::Uuid;

use crate::{
    models::transaction::Transaction,

    repositories::
        transaction_repository::
            insert_transaction,
};

pub async fn save_transactions(
    pool: &PgPool,
    statement_id: Uuid,
    txns: Vec<Transaction>,
) {
    println!(
        "Attempting to save {} transactions",
        txns.len()
    );

    for txn in txns {

        println!(
            "Saving txn: {:?}",
            txn
        );

        let raw_row =
            serde_json::json!({});

        match insert_transaction(
            pool,
            statement_id,
            &txn,
            raw_row,
        )
        .await
        {
            Ok(_) => {
                println!(
                    "INSERT SUCCESS"
                );
            }

            Err(err) => {
                println!(
                    "INSERT FAILED: {:?}",
                    err
                );
            }
        }
    }
}