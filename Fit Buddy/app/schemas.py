from typing import Literal

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    user_id: int = Field(gt=0)
    age: int = Field(ge=14, le=100)
    weight: float = Field(gt=20, le=400)
    goal: str = Field(min_length=2, max_length=200)
    intensity: Literal["low", "medium", "high"]


class FeedbackRequest(BaseModel):
    user_id: int = Field(gt=0)
    feedback: str = Field(min_length=3, max_length=500)
