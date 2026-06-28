use axum::{
    routing::{get, post},
    Router,
};
use crate::state::AppState;
use crate::handlers::statement_handler::{
    upload_statement,
    get_status,
};

pub fn statement_routes() -> Router<AppState>{

    Router::new()
        .route(
            "/api/v1/statements/upload",
            post(upload_statement),
        )
        .route(
            "/api/v1/statements/{job_id}/status",
            get(get_status),
        )
}