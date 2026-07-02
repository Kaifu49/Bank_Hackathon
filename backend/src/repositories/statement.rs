use sqlx::PgPool;
use uuid::Uuid;

pub async fn insert_statement(
    db: &PgPool,
    statement_id: Uuid,
    filename: String,
    bank_name: Option<String>,
    file_path: String,
) -> anyhow::Result<()> {

    sqlx::query(
        r#"
        INSERT INTO statements
        (
            id,
            filename,
            bank_name,
            status,
            file_path
        )
        VALUES
        (
            $1,
            $2,
            $3,
            'queued',
            $4
        )
        "#
    )
    .bind(statement_id)
    .bind(filename)
    .bind(bank_name)
    .bind(file_path)
    .execute(db)
    .await?;

    Ok(())
}

pub async fn update_statement_status(
    db: &PgPool,
    statement_id: Uuid,
    status: &str,
) -> anyhow::Result<()> {

    sqlx::query(
        r#"
        UPDATE statements
        SET status = $1
        WHERE id = $2
        "#
    )
    .bind(status)
    .bind(statement_id)
    .execute(db)
    .await?;

    Ok(())
}
