use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceHealth {
    pub service: String,
    pub status: String,
}