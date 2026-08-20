from pydantic import BaseModel, ConfigDict


class MatchCreate(BaseModel):
    team_id: int
    candidate_user_id: int
    match_score: float
    match_reasons: list[str]


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: int
    candidate_user_id: int
    match_score: float
    match_reasons: list[str]


class MatchUpdate(BaseModel):
    match_score: float | None = None
    match_reasons: list[str] | None = None
