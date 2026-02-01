"""
Whisper Speech-to-Text Service
Handles audio transcription using faster-whisper
"""
from faster_whisper import WhisperModel
from backend.config import settings
import logging
import io
import tempfile
import os

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for converting speech to text using Whisper"""

    def __init__(self):
        self.model = None
        self._model_size = settings.whisper_model_size

    def _ensure_model_loaded(self):
        """Lazy load the Whisper model"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self._model_size}")
            try:
                # Use CPU with int8 quantization for efficiency
                self.model = WhisperModel(
                    self._model_size,
                    device="cpu",
                    compute_type="int8",
                    download_root="./models/whisper"
                )
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text

        Args:
            audio_bytes: Audio data in bytes (webm, wav, mp3, etc.)

        Returns:
            Transcribed text
        """
        self._ensure_model_loaded()

        try:
            # Write audio bytes to temporary file
            # faster-whisper requires a file path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            try:
                # Transcribe the audio
                segments, info = self.model.transcribe(
                    tmp_path,
                    language="en",  # Can be made configurable
                    beam_size=5,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )

                # Combine all segments into single text
                transcription = " ".join([segment.text for segment in segments])

                logger.info(f"Transcribed {len(transcription)} characters")
                return transcription.strip()

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def change_model(self, model_size: str):
        """
        Change the Whisper model size (requires reload)

        Args:
            model_size: One of 'tiny.en', 'base.en', 'small.en', 'medium.en', 'large'
        """
        logger.info(f"Changing Whisper model from {self._model_size} to {model_size}")
        self._model_size = model_size
        self.model = None  # Force reload on next transcribe


# Global service instance
whisper_service = WhisperService()
