from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    goal_description: Mapped[str] = mapped_column(Text, nullable=False)
    member_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
