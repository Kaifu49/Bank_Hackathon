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
// Graph Intelligence (Phase 3) — DB-driven
//
// Transactions are already persisted above. The graph service reads the
// WHOLE transaction network from Postgres (across all statements), builds
// the money-flow graph, and returns money-flow + round-trips + clusters.
// This is why loops/trails appear: they span the network, not one upload.
// No Neo4j dependency for these results.
// --------------------------------

let graph_response =
    client
        .get(
            "http://localhost:8005/flow/analyze/all"
        )
        .send()
        .await;

match graph_response {

    Ok(resp) => {

        match resp.json::<Value>().await {

            Ok(graph_json) => {

                println!(
                    "\n========== GRAPH INTELLIGENCE (summary) ==========\n{}",
                    serde_json::to_string_pretty(
                        &graph_json["summary"]
                    )
                    .unwrap_or_default()
                );

                let trips =
                    graph_json["round_trips"]
                        .as_array()
                        .map(|a| a.len())
                        .unwrap_or(0);

                let communities =
                    graph_json["communities"]
                        .as_array()
                        .map(|a| a.len())
                        .unwrap_or(0);

                println!(
                    "Round-trips: {} | Communities: {}",
                    trips,
                    communities
                );
            }

            Err(err) => {
                println!(
                    "Failed to parse graph intelligence JSON: {}",
                    err
                );
            }
        }
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