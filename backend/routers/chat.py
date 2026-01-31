from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from backend.models import ChatRequest, ModelInfo
from backend.services.ollama_service import ollama_service
from backend.utils.streaming import event_generator

router = APIRouter(prefix="/api")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).

    Args:
        request: Chat request with message and optional model

    Returns:
        StreamingResponse with SSE events
    """
    try:
        # Generate streaming response from Ollama
        ollama_stream = ollama_service.generate_stream(
            prompt=request.message,
            model=request.model,
        )

        # Convert to SSE format
        sse_stream = event_generator(ollama_stream)

        return StreamingResponse(
            sse_stream,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """
    List available Ollama models.

    Returns:
        List of available models
    """
    try:
        models = await ollama_service.list_models()
        return [ModelInfo(name=model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
