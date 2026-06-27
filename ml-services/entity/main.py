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

    return {

        "count":
            len(result),

        "entities": [

            entity.model_dump()

            for entity in result
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