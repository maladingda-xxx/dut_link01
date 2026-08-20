from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TeamGapAnalysis(Base):
    __tablename__ = "team_gap_analyses"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    existing_strengths: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    missing_skills: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
