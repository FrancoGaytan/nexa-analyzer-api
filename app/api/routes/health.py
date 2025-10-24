from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check():
    """Simple health endpoint to verify the API is running."""
    return {"status": "ok"}
