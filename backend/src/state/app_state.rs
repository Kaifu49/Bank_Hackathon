use reqwest::Client;
use sqlx::PgPool;

use crate::services::queue::JobSender;
use crate::state::job_status::JobStatusStore;

#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
    pub http_client: Client,
    pub job_sender: JobSender,
    pub job_status: JobStatusStore,
}