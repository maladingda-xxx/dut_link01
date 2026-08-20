from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Connection(Base):
    __tablename__ = "connections"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('team_match', 'discovery')",
            name="ck_connections_source_type",
        ),
    )

    user_a_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user_b_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    source_type: Mapped[str] = mapped_column(String, primary_key=True)
