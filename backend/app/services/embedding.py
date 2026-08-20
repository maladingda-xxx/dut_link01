"""Local sentence-transformers embedding service.

DeepSeek exposes only a chat API (no embedding endpoint), so skill vectors are
embedded with a local multilingual model. Loaded lazily once and cached.
"""

import asyncio
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def _encode(text: str) -> list[float]:
    model = _get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def skill_vector_to_embedding_text(skill_vector: dict[str, float]) -> str:
    """Serialize a skill vector into the text embedded for similarity search."""
    return "，".join(skill_vector.keys())


async def embed_text(text: str) -> list[float]:
    """Embed text off the event loop (model load + encode both run in a thread)."""
    return await asyncio.get_running_loop().run_in_executor(None, _encode, text)
