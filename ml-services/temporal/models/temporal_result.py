from pydantic import BaseModel


class TemporalResult(BaseModel):

    account: str

    temporal_score: float

    patterns: list[str] = []