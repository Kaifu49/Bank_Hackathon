use serde::{
    Deserialize,
    Serialize,
};

#[derive(
    Debug,
    Serialize,
    Deserialize,
)]
pub struct CanonicalEntity {

    pub canonical: String,

    #[serde(default)]
    pub aliases: Vec<String>,

    #[serde(default)]
    pub entity_type:
        Option<String>,

    #[serde(default)]
    pub confidence:
        Option<f64>,
}