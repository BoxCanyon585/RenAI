from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, description="User message to send to the LLM")
    model: Optional[str] = Field(None, description="Model to use for generation (uses default if not specified)")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="LLM generated response")
    model: str = Field(..., description="Model used for generation")


class ModelInfo(BaseModel):
    """Information about an available model."""

    name: str = Field(..., description="Model name")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Health status")
    ollama: str = Field(..., description="Ollama connection status")
