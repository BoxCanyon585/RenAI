from fastapi import APIRouter
from backend.models import HealthResponse
from backend.services.ollama_service import ollama_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status and Ollama connection status
    """
    ollama_status = await ollama_service.health_check()

    return HealthResponse(
        status="healthy" if ollama_status else "degraded",
        ollama="connected" if ollama_status else "disconnected",
    )
