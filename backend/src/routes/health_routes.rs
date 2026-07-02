use axum::{
    routing::get,
    Router,
};

use crate::{
    handlers::health_handler::{
        health,
        test_ocr,
        services_health,
    },
    state::AppState,
};

pub fn health_routes() -> Router<AppState> {

    Router::new()
        .route("/health", get(health))
        .route("/test-ocr", get(test_ocr))
        .route(
            "/services/health",
            get(services_health),
        )
}