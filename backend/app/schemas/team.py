from pydantic import BaseModel, ConfigDict


class TeamCreate(BaseModel):
    name: str
    goal_description: str
    member_ids: list[int]


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    goal_description: str
    member_ids: list[int]


class TeamUpdate(BaseModel):
    name: str | None = None
    goal_description: str | None = None
    member_ids: list[int] | None = None
