use serde::{
    Serialize,
    Deserialize,
};

#[derive(
    Debug,
    Clone,
    Serialize,
    Deserialize
)]
pub struct StatementMetadata {

    pub account_number:
        Option<String>,

    pub account_holder:
        Option<String>,

    pub bank_name:
        Option<String>,

    pub ifsc_code:
        Option<String>,

    pub opening_balance:
        Option<f64>,

    pub closing_balance:
        Option<f64>,

    pub statement_start_date:
        Option<String>,

    pub statement_end_date:
        Option<String>,
}