"""Schemas for the skill-profile generation Agent (Agent 1)."""

from pydantic import BaseModel, field_validator


class PotentialDirection(BaseModel):
    """A single inferred direction with its concrete reasoning, per CLAUDE.md §4."""

    direction: str
    reasoning: str


class ProfileGenerationOutput(BaseModel):
    """Structured output contract enforced on the LLM via Pydantic validation."""

    skill_vector: dict[str, float]
    interest_tags: list[str]
    potential_directions: list[PotentialDirection]

    @field_validator("skill_vector")
    @classmethod
    def _validate_skill_vector(cls, v: dict[str, float]) -> dict[str, float]:
        if not 5 <= len(v) <= 8:
            raise ValueError(f"skill_vector 需 5~8 个维度，当前 {len(v)} 个")
        if not all(0.0 <= score <= 1.0 for score in v.values()):
            raise ValueError("skill_vector 打分必须在 0~1 之间")
        return v

    @field_validator("interest_tags")
    @classmethod
    def _validate_interest_tags(cls, v: list[str]) -> list[str]:
        if not 3 <= len(v) <= 6:
            raise ValueError(f"interest_tags 需 3~6 个，当前 {len(v)} 个")
        return v

    @field_validator("potential_directions")
    @classmethod
    def _validate_potential_directions(
        cls, v: list[PotentialDirection]
    ) -> list[PotentialDirection]:
        if not 2 <= len(v) <= 3:
            raise ValueError(f"potential_directions 需 2~3 个，当前 {len(v)} 个")
        return v


class GenerateProfileRequest(BaseModel):
    """Optional extra context merged into the agent input alongside bio_raw."""

    project_experience: str | None = None


class GenerateProfileResponse(BaseModel):
    """What the endpoint returns after generating + persisting a profile."""

    user_id: int
    skill_vector: dict[str, float]
    interest_tags: list[str]
    potential_directions: list[PotentialDirection]
    embedding_dim: int
