from pydantic import BaseModel


class Entity(
    BaseModel
):

    entity_type: str

    identifier: str

    confidence: float = 1.0