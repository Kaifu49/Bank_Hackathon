use serde_json::{json, Value};

pub async fn check_service(url: &str) -> Value {
    match reqwest::get(format!("{}/health", url)).await {
        Ok(response) => {
            match response.json::<Value>().await {
                Ok(body) => body,
                Err(_) => json!({
                    "status": "unhealthy",
                    "error": "invalid json"
                }),
            }
        }
        Err(err) => {
            json!({
                "status": "offline",
                "error": err.to_string()
            })
        }
    }
}