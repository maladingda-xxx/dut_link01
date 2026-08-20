from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    major: Mapped[str] = mapped_column(String, nullable=False)
    grade: Mapped[str] = mapped_column(String, nullable=False)
    bio_raw: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[str | None] = mapped_column(String, nullable=True)
    portfolio_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
