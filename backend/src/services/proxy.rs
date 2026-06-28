//! Thin HTTP proxy helpers: the gateway forwards analysis requests to the
//! Python ML services and returns their JSON (to be wrapped in the envelope).

use reqwest::Client;
use serde_json::Value;

use crate::api::AppError;

pub async fn get_json(client: &Client, url: &str) -> Result<Value, AppError> {
    let resp = client.get(url).send().await?;
    if !resp.status().is_success() {
        return Err(AppError::Upstream(format!(
            "{} returned {}",
            url,
            resp.status()
        )));
    }
    let body = resp.json::<Value>().await?;
    Ok(body)
}

pub async fn post_json(
    client: &Client,
    url: &str,
    payload: &Value,
) -> Result<Value, AppError> {
    let resp = client.post(url).json(payload).send().await?;
    if !resp.status().is_success() {
        return Err(AppError::Upstream(format!(
            "{} returned {}",
            url,
            resp.status()
        )));
    }
    let body = resp.json::<Value>().await?;
    Ok(body)
}
