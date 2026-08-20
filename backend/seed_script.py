"""Seed the database with fictional students and their AI-generated SkillProfiles.

Reads seed_data.json, creates each User, runs Agent 1 (profile_agent) on their
bio + project experience, and persists the resulting SkillProfile (including the
local sentence-transformers embedding). Finally prints a per-user summary so the
profiles can be eyeballed for quality.

Usage (run from backend/, with the project venv):
    ../.venv/bin/python seed_script.py            # idempotent: skips names already present
    ../.venv/bin/python seed_script.py --reset    # wipe users/skill_profiles first, then seed

Prerequisites: the DB must be migrated (alembic upgrade head) and pgvector loaded.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Make `app` importable regardless of the caller's cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import delete, select

from app.agents.profile_agent import profile_agent
from app.core.database import async_session_factory
from app.models import SkillProfile, User
from app.services.embedding import embed_text, skill_vector_to_embedding_text

SEED_DATA = Path(__file__).resolve().parent / "seed_data.json"


def load_seed() -> list[dict]:
    return json.loads(SEED_DATA.read_text(encoding="utf-8"))


async def seed(reset_first: bool) -> None:
    items = load_seed()
    async with async_session_factory() as db:
        if reset_first:
            await db.execute(delete(SkillProfile))
            await db.execute(delete(User))
            await db.commit()
            print("已清空 users / skill_profiles 表。\n")

        summaries: list[dict] = []
        for idx, item in enumerate(items, start=1):
            name, major = item["name"], item["major"]
            existing = (
                await db.execute(select(User).where(User.name == name))
            ).scalar_one_or_none()
            if existing is not None:
                print(f"[{idx:>2}/{len(items)}] 跳过已存在：{name}")
                continue

            try:
                user = User(
                    name=name,
                    major=major,
                    grade=item["grade"],
                    bio_raw=item["bio_raw"],
                    github_url=item.get("github_url"),
                    portfolio_urls=item.get("portfolio_urls"),
                )
                db.add(user)
                await db.flush()  # populate user.id

                output = await profile_agent.ainvoke(
                    user.bio_raw, item.get("project_experience")
                )
                embedding = await embed_text(
                    skill_vector_to_embedding_text(output.skill_vector)
                )

                profile = SkillProfile(
                    user_id=user.id,
                    skill_vector=output.skill_vector,
                    interest_tags=output.interest_tags,
                    potential_directions=[
                        d.direction for d in output.potential_directions
                    ],
                    embedding=embedding,
                    raw_llm_output=output.model_dump(),
                )
                db.add(profile)
                await db.commit()

                summaries.append(
                    {
                        "name": name,
                        "major": major,
                        "grade": item["grade"],
                        "output": output,
                    }
                )
                print(
                    f"[{idx:>2}/{len(items)}] ✅ {name}（{major}）"
                    f"→ skill_vector {len(output.skill_vector)} 维"
                )
            except Exception as exc:  # noqa: BLE001 — one bad profile shouldn't abort the batch
                await db.rollback()
                print(f"[{idx:>2}/{len(items)}] ❌ {name}（{major}）失败：{exc}")

        print_summaries(summaries)


def print_summaries(summaries: list[dict]) -> None:
    print("\n" + "=" * 72)
    print(f"种子用户画像摘要（共 {len(summaries)} 人）")
    print("=" * 72)
    for s in summaries:
        out = s["output"]
        print(f"\n【{s['name']}】{s['major']} · {s['grade']}")
        sv = "，".join(f"{k}:{v:.2f}" for k, v in out.skill_vector.items())
        print(f"  skill_vector: {sv}")
        print(f"  interest_tags: {', '.join(out.interest_tags)}")
        for d in out.potential_directions:
            print(f"  → {d.direction}｜{d.reasoning}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed DUT Link with fictional students.")
    parser.add_argument(
        "--reset", action="store_true", help="清空 users/skill_profiles 后重新写入"
    )
    args = parser.parse_args()
    asyncio.run(seed(reset_first=args.reset))


if __name__ == "__main__":
    main()
