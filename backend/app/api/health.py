from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Minimal liveness check used by the frontend to confirm connectivity."""
    return {"status": "ok"}
