from pydantic import BaseModel
from typing import Optional
from pydantic import Field

class Repository(BaseModel):

    name: str
    full_name: str

    description: Optional[str] = None

    stars: int

    language: Optional[str] = None

    last_update: str

    url: str

    fork: bool

    archived: bool

    topics: list[str] = Field(default_factory=list)

    homepage: Optional[str] = None

    score: int = 0

    confidence: str = "low"

    reasons: list[str] = Field(default_factory=list)

    score_breakdown: dict = Field(default_factory=dict)

    rank: int = 0

    signals: dict = Field(default_factory=dict)