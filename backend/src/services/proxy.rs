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

/// Fetch a binary download (PDF/Excel/DOCX) from an upstream service.
/// Returns (content_type, content_disposition, bytes).
pub async fn fetch_bytes(
    client: &Client,
    url: &str,
) -> Result<(String, Option<String>, Vec<u8>), AppError> {
    let resp = client.get(url).send().await?;
    if !resp.status().is_success() {
        return Err(AppError::Upstream(format!(
            "{} returned {}",
            url,
            resp.status()
        )));
    }
    let content_type = resp
        .headers()
        .get(reqwest::header::CONTENT_TYPE)
        .and_then(|v| v.to_str().ok())
        .unwrap_or("application/octet-stream")
        .to_string();
    let disposition = resp
        .headers()
        .get(reqwest::header::CONTENT_DISPOSITION)
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string());
    let bytes = resp.bytes().await?.to_vec();
    Ok((content_type, disposition, bytes))
}
