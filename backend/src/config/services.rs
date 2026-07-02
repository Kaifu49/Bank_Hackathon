pub struct ServiceRegistry {
    pub ocr: &'static str,
    pub standardize: &'static str,
    pub entity: &'static str,
    pub anomaly: &'static str,
    pub temporal: &'static str,
    pub graph_ml: &'static str,
    pub explainer: &'static str,
}

pub const SERVICES: ServiceRegistry = ServiceRegistry {
    ocr: "http://localhost:8001",
    standardize: "http://localhost:8002",
    entity: "http://localhost:8003",
    anomaly: "http://localhost:8004",
    temporal: "http://localhost:8005",
    graph_ml: "http://localhost:8006",
    explainer: "http://localhost:8007",
};
