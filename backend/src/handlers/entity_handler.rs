use axum::extract::{Path, Query, State};
use serde::Deserialize;
use serde_json::{json, Value};

use crate::{
    api::{ApiResponse, ApiResult, Pagination},
    repositories::read_repository,
    state::app_state::AppState,
};

// Flat struct (serde_urlencoded used by Query does NOT support #[serde(flatten)]).
#[derive(Debug, Deserialize)]
pub struct EntityFilter {
    #[serde(rename = "type")]
    pub entity_type: Option<String>,
    pub page: Option<i64>,
    pub page_size: Option<i64>,
}

/// GET /api/v1/entities?type=UPI_ID&page=1&page_size=50
pub async fn list_entities(
    State(state): State<AppState>,
    Query(filter): Query<EntityFilter>,
) -> ApiResult<Vec<Value>> {
    let page = Pagination { page: filter.page, page_size: filter.page_size };
    let total = read_repository::count_entities(&state.db, &filter.entity_type).await?;
    let items = read_repository::list_entities(
        &state.db,
        &filter.entity_type,
        page.page_size(),
        page.offset(),
    )
    .await?;
    Ok(ApiResponse::success_paginated(items, page.meta(total)))
}

/// GET /api/v1/entities/{id}
pub async fn get_entity(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Value> {
    let e = read_repository::get_entity(&state.db, &id).await?;
    Ok(ApiResponse::success(e))
}

/// GET /api/v1/entities/{id}/aliases
pub async fn get_entity_aliases(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Value> {
    let e = read_repository::get_entity(&state.db, &id).await?;
    let aliases = e
        .get("metadata")
        .and_then(|m| m.get("aliases"))
        .cloned()
        .unwrap_or(json!([]));
    Ok(ApiResponse::success(json!({
        "id": e.get("id"),
        "identifier": e.get("identifier"),
        "aliases": aliases
    })))
}
