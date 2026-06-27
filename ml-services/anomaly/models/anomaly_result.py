from pydantic import BaseModel


class AnomalyResult(BaseModel):

    account: str

    stat_score: float

    patterns: list[str] = []