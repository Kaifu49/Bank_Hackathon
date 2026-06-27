use std::{
    collections::HashMap,
    sync::Arc,
};

use tokio::sync::RwLock;
use uuid::Uuid;

pub type JobStatusStore =
    Arc<RwLock<HashMap<Uuid, String>>>;