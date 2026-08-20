from typing import Any

from pydantic import BaseModel, ConfigDict


class SkillProfileCreate(BaseModel):
    user_id: int
    skill_vector: dict[str, float]
    interest_tags: list[str]
    potential_directions: list[str]
    embedding: list[float] | None = None
    raw_llm_output: dict[str, Any]


class SkillProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    skill_vector: dict[str, float]
    interest_tags: list[str]
    potential_directions: list[str]
    embedding: list[float] | None
    raw_llm_output: dict[str, Any]


class SkillProfileUpdate(BaseModel):
    skill_vector: dict[str, float] | None = None
    interest_tags: list[str] | None = None
    potential_directions: list[str] | None = None
    embedding: list[float] | None = None
    raw_llm_output: dict[str, Any] | None = None
