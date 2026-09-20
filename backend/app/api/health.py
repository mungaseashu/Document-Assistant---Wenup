from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    environment: str

@router.get("/health", response_model=HealthResponse)
async def check_health():
    return HealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT
    )
