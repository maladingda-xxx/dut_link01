from pydantic import BaseModel, ConfigDict


class DiscoveryCardCreate(BaseModel):
    target_user_id: int
    content_title: str
    content_reason: str
    suggested_connection_user_id: int | None = None
    connection_reason: str | None = None


class DiscoveryCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_user_id: int
    content_title: str
    content_reason: str
    suggested_connection_user_id: int | None
    connection_reason: str | None


class DiscoveryCardUpdate(BaseModel):
    content_title: str | None = None
    content_reason: str | None = None
    suggested_connection_user_id: int | None = None
    connection_reason: str | None = None
