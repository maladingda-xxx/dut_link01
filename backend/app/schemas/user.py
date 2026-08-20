from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    major: str
    grade: str
    bio_raw: str
    github_url: str | None = None
    portfolio_urls: list[str] | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    major: str
    grade: str
    bio_raw: str
    github_url: str | None
    portfolio_urls: list[str] | None


class UserUpdate(BaseModel):
    name: str | None = None
    major: str | None = None
    grade: str | None = None
    bio_raw: str | None = None
    github_url: str | None = None
    portfolio_urls: list[str] | None = None
