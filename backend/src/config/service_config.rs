//! Env-driven base URLs for the Python ML services (replaces the stale static
//! registry whose ports drifted from reality). Override any with an env var.

#[derive(Clone, Debug)]
pub struct ServiceConfig {
    pub ocr: String,
    pub standardize: String,
    pub entity: String,
    pub validation: String,
    pub graph: String,
    pub anomaly: String,
    pub temporal: String,
    pub trail: String,
    pub report: String,
}

fn env_or(key: &str, default: &str) -> String {
    std::env::var(key).unwrap_or_else(|_| default.to_string())
}

impl ServiceConfig {
    pub fn from_env() -> Self {
        ServiceConfig {
            ocr: env_or("OCR_URL", "http://localhost:8001"),
            standardize: env_or("STANDARDIZE_URL", "http://localhost:8002"),
            entity: env_or("ENTITY_URL", "http://localhost:8003"),
            validation: env_or("VALIDATION_URL", "http://localhost:8004"),
            graph: env_or("GRAPH_URL", "http://localhost:8005"),
            anomaly: env_or("ANOMALY_URL", "http://localhost:8007"),
            temporal: env_or("TEMPORAL_URL", "http://localhost:8008"),
            trail: env_or("TRAIL_URL", "http://localhost:8009"),
            report: env_or("REPORT_URL", "http://localhost:8010"),
        }
    }
}
