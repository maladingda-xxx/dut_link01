from typing import Literal

from pydantic import BaseModel, ConfigDict


class ConnectionCreate(BaseModel):
    user_a_id: int
    user_b_id: int
    source_type: Literal["team_match", "discovery"]


class ConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_a_id: int
    user_b_id: int
    source_type: Literal["team_match", "discovery"]
