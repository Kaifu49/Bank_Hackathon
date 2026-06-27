from fastapi import FastAPI
from pydantic import BaseModel

from services.entity_extractor import (
    EntityExtractor
)

from services.entity_resolver import (
    EntityResolver
)

resolver = (
    EntityResolver()
)


app = FastAPI()

extractor = (
    EntityExtractor()
)


class EntityRequest(
    BaseModel
):
    transactions: list


@app.get("/health")
def health():

    return {

        "service":
            "entity",

        "status":
            "healthy"
    }


@app.post("/entities")
def entities(
    request: EntityRequest
):

    result = (
        extractor.extract(
            request.transactions
        )
    )

    # extractor returns one mention per occurrence; dedup for display
    seen = {}
    for entity in result:
        key = (entity.entity_type, entity.identifier.upper())
        if key not in seen:
            seen[key] = entity

    unique = list(seen.values())

    return {

        "count":
            len(unique),

        "entities": [

            entity.model_dump()

            for entity in unique
        ]
    }

@app.post("/resolve")
def resolve(
    request: EntityRequest
):

    entities = (
        extractor.extract(
            request.transactions
        )
    )

    resolved = (
        resolver.resolve(
            entities
        )
    )

    return {

        "raw_count":
            len(entities),

        "canonical_entities":
            resolved
    }