from pydantic import BaseModel, ConfigDict


class TeamGapAnalysisCreate(BaseModel):
    team_id: int
    existing_strengths: list[str]
    missing_skills: list[str]


class TeamGapAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: int
    existing_strengths: list[str]
    missing_skills: list[str]


class TeamGapAnalysisUpdate(BaseModel):
    existing_strengths: list[str] | None = None
    missing_skills: list[str] | None = None
