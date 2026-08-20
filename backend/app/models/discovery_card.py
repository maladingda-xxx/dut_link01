from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DiscoveryCard(Base):
    __tablename__ = "discovery_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_title: Mapped[str] = mapped_column(String, nullable=False)
    content_reason: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_connection_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    connection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
