from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR

from app.core.database import Base


class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_vector: Mapped[dict[str, float]] = mapped_column(JSONB, nullable=False)
    interest_tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    potential_directions: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    # Dimension matches settings.embedding_dim (paraphrase-multilingual-MiniLM-L12-v2 = 384).
    embedding: Mapped[list[float] | None] = mapped_column(VECTOR(384), nullable=True)
    raw_llm_output: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
