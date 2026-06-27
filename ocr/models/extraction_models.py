from pydantic import BaseModel
from typing import Any


class ExtractedDocument(BaseModel):
    source_type: str
    filename: str
    rows: list[Any]