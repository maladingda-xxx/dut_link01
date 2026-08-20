"""initial tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import VECTOR

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("major", sa.String(), nullable=False),
        sa.Column("grade", sa.String(), nullable=False),
        sa.Column("bio_raw", sa.Text(), nullable=False),
        sa.Column("github_url", sa.String(), nullable=True),
        sa.Column("portfolio_urls", postgresql.ARRAY(sa.String()), nullable=True),
    )

    op.create_table(
        "skill_profiles",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("skill_vector", postgresql.JSONB(), nullable=False),
        sa.Column("interest_tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("potential_directions", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("embedding", VECTOR(384), nullable=True),
        sa.Column("raw_llm_output", postgresql.JSONB(), nullable=False),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("goal_description", sa.Text(), nullable=False),
        sa.Column("member_ids", postgresql.ARRAY(sa.Integer()), nullable=False),
    )

    op.create_table(
        "team_gap_analyses",
        sa.Column(
            "team_id",
            sa.Integer(),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("existing_strengths", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("missing_skills", postgresql.ARRAY(sa.String()), nullable=False),
    )

    op.create_table(
        "matches",
        sa.Column(
            "team_id",
            sa.Integer(),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "candidate_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("match_reasons", postgresql.ARRAY(sa.String()), nullable=False),
    )

    op.create_table(
        "discovery_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "target_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content_title", sa.String(), nullable=False),
        sa.Column("content_reason", sa.Text(), nullable=False),
        sa.Column(
            "suggested_connection_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("connection_reason", sa.Text(), nullable=True),
    )

    op.create_table(
        "connections",
        sa.Column(
            "user_a_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_b_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("source_type", sa.String(), primary_key=True),
        sa.CheckConstraint(
            "source_type IN ('team_match', 'discovery')",
            name="ck_connections_source_type",
        ),
    )


def downgrade() -> None:
    op.drop_table("connections")
    op.drop_table("discovery_cards")
    op.drop_table("matches")
    op.drop_table("team_gap_analyses")
    op.drop_table("teams")
    op.drop_table("skill_profiles")
    op.drop_table("users")
