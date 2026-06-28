//! API contract primitives shared by every endpoint:
//!   * `ApiResponse<T>` — the uniform success envelope
//!   * `AppError`       — the uniform error type (maps to the error envelope)
//!   * `Pagination` / `PageMeta` — list pagination
//!
//! Every handler returns `Result<ApiResponse<T>, AppError>`, so successes and
//! failures always serialize to the same shape.

use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::{Deserialize, Serialize};
use serde_json::json;
use uuid::Uuid;

// --------------------------------------------------------------------------
// Success envelope
// --------------------------------------------------------------------------

#[derive(Debug, Serialize)]
pub struct Meta {
    pub request_id: Uuid,
    pub timestamp: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pagination: Option<PageMeta>,
}

impl Meta {
    pub fn new() -> Self {
        Meta {
            request_id: Uuid::new_v4(),
            timestamp: chrono::Utc::now().to_rfc3339(),
            pagination: None,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<serde_json::Value>,
    pub meta: Meta,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        ApiResponse { success: true, data: Some(data), error: None, meta: Meta::new() }
    }

    pub fn success_paginated(data: T, pagination: PageMeta) -> Self {
        let mut meta = Meta::new();
        meta.pagination = Some(pagination);
        ApiResponse { success: true, data: Some(data), error: None, meta }
    }
}

impl<T: Serialize> IntoResponse for ApiResponse<T> {
    fn into_response(self) -> Response {
        (StatusCode::OK, Json(self)).into_response()
    }
}

// --------------------------------------------------------------------------
// Pagination
// --------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub struct Pagination {
    #[serde(default)]
    pub page: Option<i64>,
    #[serde(default)]
    pub page_size: Option<i64>,
}

impl Pagination {
    pub fn page(&self) -> i64 {
        self.page.unwrap_or(1).max(1)
    }
    pub fn page_size(&self) -> i64 {
        self.page_size.unwrap_or(50).clamp(1, 200)
    }
    pub fn offset(&self) -> i64 {
        (self.page() - 1) * self.page_size()
    }
    pub fn meta(&self, total_items: i64) -> PageMeta {
        let ps = self.page_size();
        let total_pages = if ps > 0 { (total_items + ps - 1) / ps } else { 0 };
        PageMeta {
            page: self.page(),
            page_size: ps,
            total_items,
            total_pages,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct PageMeta {
    pub page: i64,
    pub page_size: i64,
    pub total_items: i64,
    pub total_pages: i64,
}

// --------------------------------------------------------------------------
// Error envelope
// --------------------------------------------------------------------------

#[derive(Debug)]
pub enum AppError {
    Validation(String),
    UnsupportedMediaType(String),
    NotFound(String),
    Upstream(String),
    Timeout(String),
    NotImplemented(String),
    Internal(String),
}

impl AppError {
    fn parts(&self) -> (StatusCode, &'static str, String) {
        match self {
            AppError::Validation(m) => (StatusCode::BAD_REQUEST, "VALIDATION_ERROR", m.clone()),
            AppError::UnsupportedMediaType(m) => (StatusCode::UNSUPPORTED_MEDIA_TYPE, "UNSUPPORTED_MEDIA_TYPE", m.clone()),
            AppError::NotFound(m) => (StatusCode::NOT_FOUND, "NOT_FOUND", m.clone()),
            AppError::Upstream(m) => (StatusCode::BAD_GATEWAY, "UPSTREAM_SERVICE_ERROR", m.clone()),
            AppError::Timeout(m) => (StatusCode::GATEWAY_TIMEOUT, "TIMEOUT", m.clone()),
            AppError::NotImplemented(m) => (StatusCode::NOT_IMPLEMENTED, "NOT_IMPLEMENTED", m.clone()),
            AppError::Internal(m) => (StatusCode::INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", m.clone()),
        }
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, code, message) = self.parts();
        let body = json!({
            "success": false,
            "data": null,
            "error": { "code": code, "message": message, "details": {} },
            "meta": {
                "request_id": Uuid::new_v4(),
                "timestamp": chrono::Utc::now().to_rfc3339()
            }
        });
        (status, Json(body)).into_response()
    }
}

// Allow `?` on common error types inside handlers.
impl From<sqlx::Error> for AppError {
    fn from(e: sqlx::Error) -> Self {
        match e {
            sqlx::Error::RowNotFound => AppError::NotFound("resource not found".into()),
            other => AppError::Internal(format!("database error: {}", other)),
        }
    }
}

impl From<reqwest::Error> for AppError {
    fn from(e: reqwest::Error) -> Self {
        if e.is_timeout() {
            AppError::Timeout(format!("upstream timed out: {}", e))
        } else {
            AppError::Upstream(format!("upstream service error: {}", e))
        }
    }
}

impl From<anyhow::Error> for AppError {
    fn from(e: anyhow::Error) -> Self {
        AppError::Internal(e.to_string())
    }
}

pub type ApiResult<T> = Result<ApiResponse<T>, AppError>;
