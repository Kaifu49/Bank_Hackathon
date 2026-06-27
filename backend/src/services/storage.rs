use std::path::PathBuf;
use tokio::fs;
use uuid::Uuid;

pub async fn create_statement_directory(
    statement_id: Uuid,
) -> anyhow::Result<PathBuf> {

    let path = PathBuf::from(format!(
        "storage/statements/{}",
        statement_id
    ));

    fs::create_dir_all(&path).await?;

    Ok(path)
}