use sqlx::PgPool;

use crate::{
    models::entity::CanonicalEntity,
    repositories::entity_repository::upsert_entity,
};

pub async fn save_entities(
    pool: &PgPool,
    entities: Vec<CanonicalEntity>,
) {
    for entity in entities {
        if let Err(err) =
            upsert_entity(pool, &entity).await
        {
            println!(
                "Entity Save Error: {}",
                err
            );
        }
    }
}
