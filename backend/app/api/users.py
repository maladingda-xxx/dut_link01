"""User endpoints."""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.profile_agent import profile_agent
from app.api.deps import get_session
from app.models.skill_profile import SkillProfile
from app.models.user import User
from app.schemas.profile import GenerateProfileRequest, GenerateProfileResponse
from app.services.embedding import embed_text, skill_vector_to_embedding_text

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/{user_id}/generate-profile", response_model=GenerateProfileResponse)
async def generate_profile(
    user_id: int,
    body: GenerateProfileRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_session),
) -> GenerateProfileResponse:
    """Run Agent 1 on a user's bio and persist the resulting SkillProfile."""
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    project_experience = body.project_experience if body else None
    output = await profile_agent.ainvoke(user.bio_raw, project_experience)

    embedding = await embed_text(skill_vector_to_embedding_text(output.skill_vector))

    profile = await db.get(SkillProfile, user_id)
    if profile is None:
        profile = SkillProfile(user_id=user_id)
        db.add(profile)

    profile.skill_vector = output.skill_vector
    profile.interest_tags = output.interest_tags
    profile.potential_directions = [d.direction for d in output.potential_directions]
    profile.embedding = embedding
    profile.raw_llm_output = output.model_dump()
    await db.commit()

    return GenerateProfileResponse(
        user_id=user_id,
        skill_vector=output.skill_vector,
        interest_tags=output.interest_tags,
        potential_directions=output.potential_directions,
        embedding_dim=len(embedding),
    )
