use tokio::sync::mpsc;
use crate::models::statement::ProcessingJob;

pub type JobSender = mpsc::Sender<ProcessingJob>;
pub type JobReceiver = mpsc::Receiver<ProcessingJob>;