use axum::{
    extract::{
        Multipart,
        Path,
        State,
    },
    Json,
};

use axum::http::StatusCode;

use uuid::Uuid;

use crate::{
    models::statement::{
        ProcessingJob,
        StatusResponse,
        UploadResponse,
    },
    repositories::statement::insert_statement,
    services::storage::create_statement_directory,
    state::app_state::AppState,
};

pub async fn upload_statement(
    State(state): State<AppState>,
    mut multipart: Multipart,
) -> Json<UploadResponse> {

    let mut bank_name: Option<String> = None;

    let statement_id = Uuid::new_v4();
    let job_id = Uuid::new_v4();

    let mut filename = String::from("unknown");

    let mut saved_file_path: Option<std::path::PathBuf> = None;

    while let Some(field) =
        multipart
            .next_field()
            .await
            .expect(
                "Failed to read multipart field"
            )
    {

        if field.name() == Some("bank_name") {

            let value =
                field.text().await.expect(
                    "Failed to read bank name"
                );

            bank_name = Some(value);

            continue;
        }

        if field.name() == Some("file") {

            filename = field
                .file_name()
                .unwrap_or("statement")
                .to_string();

            // Validate by file EXTENSION (clients set content-types
            // inconsistently; the OCR parser registry keys on extension anyway).
            // NOTE: panic here is temporary — Phase 0 replaces it with a typed
            // 415 error in the standard response envelope.
            let extension = std::path::Path::new(&filename)
                .extension()
                .and_then(|e| e.to_str())
                .map(|e| e.to_lowercase())
                .unwrap_or_default();

            let allowed_extensions = [
                "pdf", "csv", "xlsx", "xls", "docx",
                "txt", "png", "jpg", "jpeg",
            ];

            if !allowed_extensions.contains(&extension.as_str()) {

                panic!(
                    "Unsupported file type: {}",
                    extension
                );
            }

            let bytes = field
                .bytes()
                .await
                .expect(
                    "Failed to read uploaded file"
                );

            let directory =
                create_statement_directory(
                    statement_id
                )
                .await
                .expect(
                    "Failed to create statement directory"
                );

            let file_path =
                directory.join(&filename);

            tokio::fs::write(
                &file_path,
                bytes,
            )
            .await
            .expect(
                "Failed to save uploaded file"
            );

            saved_file_path = Some(file_path);
        }
    }

    let file_path =
        saved_file_path
            .expect("No file uploaded");

    insert_statement(
        &state.db,
        statement_id,
        filename.clone(),
        bank_name.clone(),
        file_path.to_string_lossy().to_string(),
    )
    .await
    .expect(
        "Failed to insert statement into database"
    );

    let job = ProcessingJob {
        job_id,
        statement_id,
        file_path: file_path
            .to_string_lossy()
            .to_string(),
    };

    state
        .job_sender
        .send(job)
        .await
        .expect(
            "Failed to enqueue processing job"
        );

    state
        .job_status
        .write()
        .await
        .insert(
            job_id,
            String::from("queued"),
        );

    Json(UploadResponse {
        job_id,
        statement_id,
        status: String::from("queued"),
    })
}


pub async fn get_status(
    Path(job_id): Path<Uuid>,
    State(state): State<AppState>,
) -> Json<StatusResponse> {

    let status = state
        .job_status
        .read()
        .await
        .get(&job_id)
        .cloned()
        .unwrap_or_else(|| {
            String::from("unknown")
        });

    Json(StatusResponse {
        job_id,
        status,
        progress: 0,
        error: None,
    })
}