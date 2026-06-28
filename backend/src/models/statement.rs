use serde::Serialize;
use uuid::Uuid;

#[derive(Debug, Serialize)]
pub struct UploadResponse {
    pub job_id: Uuid,
    pub statement_id: Uuid,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct StatusResponse {
    pub job_id: Uuid,
    pub status: String,
    pub progress: u8,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub struct ProcessingJob {
    pub job_id: Uuid,
    pub statement_id: Uuid,
    pub file_path: String,
}

