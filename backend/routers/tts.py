"""
Text-to-Speech API Router
Handles speech synthesis endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services.piper_service import piper_service
import logging
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["text-to-speech"])


class TTSRequest(BaseModel):
    """Request model for TTS synthesis"""
    text: str
    voice: str = "default"  # Future: support multiple voices


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech using Piper TTS

    Args:
        request: TTSRequest with text to synthesize

    Returns:
        audio/wav stream
    """
    logger.info(f"TTS request: {len(request.text)} characters")

    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(request.text) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Text too long (max 5000 characters)"
        )

    try:
        # Synthesize speech
        audio_bytes = await piper_service.synthesize(request.text)

        # Return as streaming audio
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(audio_bytes))
            }
        )

    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to synthesize speech: {str(e)}"
        )


@router.get("/voices")
async def list_voices():
    """
    List available TTS voices

    Returns:
        {"voices": [...]}
    """
    # For now, return a single default voice
    # In the future, this could scan models/piper/ for multiple voices
    return {
        "voices": [
            {
                "id": "default",
                "name": "English US (Lessac Medium)",
                "language": "en-US"
            }
        ]
    }
