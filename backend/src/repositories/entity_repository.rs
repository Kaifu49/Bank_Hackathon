use sqlx::PgPool;
use uuid::Uuid;

use crate::models::entity::CanonicalEntity;

pub async fn upsert_entity(
    pool: &PgPool,
    entity: &CanonicalEntity,
) -> Result<(), sqlx::Error> {
    let metadata = serde_json::json!({
        "aliases": entity.aliases,
        "confidence": entity.confidence,
    });

    sqlx::query(
        r#"
        INSERT INTO entities (
            id,
            entity_type,
            identifier,
            display_name,
            metadata
        )
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (identifier)
        DO UPDATE SET
            entity_type = EXCLUDED.entity_type,
            display_name = EXCLUDED.display_name,
            metadata = EXCLUDED.metadata
        "#,
    )
    .bind(Uuid::new_v4())
    .bind(
    entity
        .entity_type
        .clone()
        .unwrap_or_else(
            || "UNKNOWN".to_string()
        )
)
    .bind(&entity.canonical)
    .bind(&entity.canonical)
    .bind(metadata)
    .execute(pool)
    .await?;

    Ok(())
}
