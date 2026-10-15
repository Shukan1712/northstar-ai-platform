from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1500)
    customer_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    mode: str
    tools_used: list[str]
    citations: list[dict[str, Any]]
    limitations: list[str]
    latency_ms: int

