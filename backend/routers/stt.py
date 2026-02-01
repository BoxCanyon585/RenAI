"""
Speech-to-Text API Router
Handles audio transcription endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from backend.services.whisper_service import whisper_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stt", tags=["speech-to-text"])


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file to text using Whisper

    Accepts: audio/webm, audio/wav, audio/mp3, audio/ogg
    Returns: {"text": "transcribed text"}
    """
    logger.info(f"Received transcription request: {audio.filename}, content_type: {audio.content_type}")

    # Validate content type
    valid_types = [
        "audio/webm",
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/mp3",
        "audio/mpeg",
        "audio/ogg",
        "audio/x-m4a"
    ]

    if audio.content_type and audio.content_type not in valid_types:
        logger.warning(f"Invalid content type: {audio.content_type}")
        # Don't reject - Whisper can handle many formats
        # Just log the warning

    try:
        # Read audio bytes
        audio_bytes = await audio.read()

        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        logger.info(f"Audio file size: {len(audio_bytes)} bytes")

        # Transcribe
        text = await whisper_service.transcribe(audio_bytes)

        if not text:
            return JSONResponse(
                content={"text": "", "warning": "No speech detected in audio"},
                status_code=200
            )

        return JSONResponse(
            content={"text": text},
            status_code=200
        )

    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@router.post("/change-model")
async def change_whisper_model(model_size: str):
    """
    Change the Whisper model size

    Args:
        model_size: One of 'tiny.en', 'base.en', 'small.en', 'medium.en'

    Returns:
        {"status": "success", "model": model_size}
    """
    valid_models = ["tiny.en", "base.en", "small.en", "medium.en", "large"]

    if model_size not in valid_models:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model size. Must be one of: {', '.join(valid_models)}"
        )

    try:
        whisper_service.change_model(model_size)
        return JSONResponse(
            content={"status": "success", "model": model_size},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Failed to change model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change model: {str(e)}"
        )
