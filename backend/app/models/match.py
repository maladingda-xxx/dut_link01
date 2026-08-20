from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Match(Base):
    __tablename__ = "matches"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    candidate_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
