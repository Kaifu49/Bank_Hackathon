use serde::{
    Deserialize,
    Serialize,
};

#[derive(
    Debug,
    Serialize,
    Deserialize,
)]
pub struct Transaction {

    pub date: Option<String>,

    pub amount: Option<f64>,

    pub txn_type: Option<String>,

    pub reference_number:
        Option<String>,

    pub narration:
        Option<String>,

    pub narration_normalized:
        Option<String>,

    pub balance:
        Option<f64>,

    pub debit_credit:
        Option<String>,

    pub platform:
        Option<String>,

    pub upi_id:
        Option<String>,

    pub sender_account:
    Option<String>,

    pub receiver_account:
        Option<String>,

    pub bank_name:
        Option<String>,

    pub is_duplicate:
        Option<bool>,

    pub is_failed:
        Option<bool>,

    pub is_valid:
        Option<bool>,

    pub confidence_score:
        Option<f64>,

    pub validation_notes:
        Option<Vec<String>>,
}