use crate::{
    models::{
        statement::ProcessingJob,
        transaction::Transaction,
        entity::CanonicalEntity,
    },
    services::{
        transaction_service::save_transactions,
        entity_service::save_entities,
    },
};

use reqwest::Client;
use serde_json::Value;
use sqlx::PgPool;

pub async fn start_worker(
    mut receiver: tokio::sync::mpsc::Receiver<
        ProcessingJob,
    >,
    db: PgPool,
) {
    let client = Client::new();

    while let Some(job) =
        receiver.recv().await
    {
        println!(
            "\nProcessing statement: {}",
            job.statement_id
        );

        println!("Status: processing");

        println!(
            "Sending file path to OCR:\n{}",
            job.file_path
        );

        let absolute_path =
            std::fs::canonicalize(
                &job.file_path
            )
            .unwrap()
            .to_string_lossy()
            .to_string();

        let ocr_response = client
            .post(
                "http://localhost:8001/extract"
            )
            .json(&serde_json::json!({
                "file_path": absolute_path
            }))
            .send()
            .await;

        match ocr_response {

            Ok(resp) => {

                let ocr_json: Value =
                    match resp.json().await {

                        Ok(data) => data,

                        Err(err) => {

                            println!(
                                "Failed to parse OCR JSON: {}",
                                err
                            );

                            continue;
                        }
                    };

                println!(
                    "\n========== OCR OUTPUT ==========\n{}",
                    serde_json::to_string_pretty(
                        &ocr_json
                    )
                    .unwrap()
                );

                let standardize_response =
                    client
                        .post(
                            "http://localhost:8002/standardize"
                        )
                        .json(
                            &serde_json::json!({
                                "rows": ocr_json["rows"]
                            })
                        )
                        .send()
                        .await;

                match standardize_response {

                    Ok(resp) => {

                        let standardized_json: Value =
                            match resp.json().await {

                                Ok(data) => data,

                                Err(err) => {

                                    println!(
                                        "Failed to parse standardized JSON: {}",
                                        err
                                    );

                                    continue;
                                }
                            };

                        println!(
                            "\n========== STANDARDIZED OUTPUT ==========\n{}",
                        
                            


                            serde_json::to_string_pretty(
                                &standardized_json
                            )
                            .unwrap()
                        );

                        // --------------------------------
// Validation Service
// --------------------------------

let validation_response =
    client
        .post(
            "http://localhost:8004/validate"
        )
        .json(
            &serde_json::json!({
                "transactions":
                    standardized_json[
                        "transactions"
                    ]
            })
        )
        .send()
        .await;

match validation_response {

    Ok(resp) => {

        let validated_json: Value =
            match resp.json().await {

                Ok(data) => data,

                Err(err) => {

                    println!(
                        "Failed to parse validation JSON: {}",
                        err
                    );

                    continue;
                }
            };

        println!(
            "\n========== VALIDATION OUTPUT ==========\n{}",
            serde_json::to_string_pretty(
                &validated_json
            )
            .unwrap()
        );

        println!(
    "\nFIRST VALIDATED TXN:\n{}",
    serde_json::to_string_pretty(
        &validated_json["transactions"][0]
    )
    .unwrap()
);

        // --------------------------------
        // Deserialize Transactions
        // --------------------------------

        let transactions:
            Vec<Transaction> =

            serde_json::from_value(
                validated_json[
                    "transactions"
                ]
                .clone()
            )
            .unwrap_or_default();

        println!(
            "Parsed {} validated transactions",
            transactions.len()
        );

        // --------------------------------
        // Save Transactions
        // --------------------------------

        save_transactions(
    &db,
    job.statement_id,
    transactions,
)
.await;

println!(
    "Validated transactions saved successfully"
);

// --------------------------------
// Entity Extraction Service
// --------------------------------

let entity_response =
    client
        .post(
            "http://localhost:8003/resolve"
        )
        .json(
            &serde_json::json!({
                "transactions":
                    validated_json[
                        "transactions"
                    ]
            })
        )
        .send()
        .await;

match entity_response {

    Ok(resp) => {

        let entity_json: Value =
            match resp.json().await {

                Ok(data) => data,

                Err(err) => {

                    println!(
                        "Failed to parse entity JSON: {}",
                        err
                    );

                    continue;
                }
            };

        println!(
            "\n========== ENTITY OUTPUT ==========\n{}",
            serde_json::to_string_pretty(
                &entity_json
            )
            .unwrap()
        );

        let entities:
            Vec<CanonicalEntity> =
                serde_json::from_value(
                    entity_json[
                        "canonical_entities"
                    ]
                    .clone()
                )
                .unwrap_or_default();

        println!(
            "Parsed {} canonical entities",
            entities.len()
        );

        save_entities(
    &db,
    entities,
)
.await;

println!(
    "Entities saved successfully"
);

// --------------------------------
// Neo4j Graph Builder
// --------------------------------

// --------------------------------
// Account Graph Builder
// --------------------------------

let account_graph_response =
    client
        .post(
            "http://localhost:8005/build-graph"
        )
        .json(
            &serde_json::json!({
                "transactions":
                    validated_json[
                        "transactions"
                    ]
            })
        )
        .send()
        .await;

match account_graph_response {

    Ok(resp) => {

        let graph_json: Value =
            match resp.json().await {

                Ok(data) => data,

                Err(err) => {

                    println!(
                        "Failed to parse account graph response: {}",
                        err
                    );

                    continue;
                }
            };

        println!(
            "\n========== ACCOUNT GRAPH OUTPUT ==========\n{}",
            serde_json::to_string_pretty(
                &graph_json
            )
            .unwrap()
        );
    }

    Err(err) => {

        println!(
            "Account Graph Error: {}",
            err
        );
    }
}

let graph_response =
    client
        .post(
            "http://localhost:8005/build-transaction-graph"
        )
        .json(
            &serde_json::json!({

                "transactions":
                    validated_json[
                        "transactions"
                    ],

                "entities":
                    entity_json[
                        "canonical_entities"
                    ]
            })
        )
        .send()
        .await;

match graph_response {

    Ok(resp) => {

        let graph_json: Value =
            match resp.json().await {

                Ok(data) => data,

                Err(err) => {

                    println!(
                        "Failed to parse graph JSON: {}",
                        err
                    );

                    continue;
                }
            };

        println!(
            "\n========== GRAPH OUTPUT ==========\n{}",
            serde_json::to_string_pretty(
                &graph_json
            )
            .unwrap()
        );
    }

    Err(err) => {

        println!(
            "Graph Service Error: {}",
            err
        );
    }
}
    }

    Err(err) => {

        println!(
            "Entity Service Error: {}",
            err
        );
    }
}
    }



    Err(err) => {

        println!(
            "Validation Service Error: {}",
            err
        );
    }
}

                        println!(
                            "Transactions saved successfully"
                        );

                        println!(
                            "\nStatus: completed"
                        );
                    }

                    Err(err) => {

                        println!(
                            "Standardizer Error: {}",
                            err
                        );
                    }
                }
            }

            Err(err) => {

                println!(
                    "OCR Service Error: {}",
                    err
                );
            }
        }
    }
}