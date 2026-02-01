"""
Piper Text-to-Speech Service
Handles text-to-speech synthesis using Piper TTS
"""
import logging
import io
import wave
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Note: piper-tts is typically used via command-line
# For Python integration, we'll use subprocess to call piper binary
# Alternatively, we can use the piper Python bindings if available
import subprocess


class PiperService:
    """Service for converting text to speech using Piper"""

    def __init__(self):
        self.model_path = None
        self.config_path = None
        self._ensure_model_paths()

    def _ensure_model_paths(self):
        """Ensure Piper model and config files exist"""
        models_dir = Path("./models/piper")

        # Look for .onnx model file
        onnx_files = list(models_dir.glob("*.onnx"))
        if onnx_files:
            self.model_path = str(onnx_files[0])
            # Config file should be model_name.onnx.json
            self.config_path = f"{self.model_path}.json"
            logger.info(f"Using Piper model: {self.model_path}")
        else:
            logger.warning("No Piper model found in models/piper/")

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio

        Args:
            text: Text to convert to speech

        Returns:
            Audio bytes in WAV format
        """
        if not self.model_path:
            raise Exception("Piper model not found. Please download the model first.")

        try:
            # Use piper binary to synthesize
            # piper --model <model.onnx> --output_file <output.wav>
            # Or pipe text to stdin and get WAV from stdout

            # Create output buffer
            output_buffer = io.BytesIO()

            # Try to use piper via subprocess
            # Check if piper is installed
            try:
                result = subprocess.run(
                    ['piper', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                piper_installed = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                piper_installed = False

            if not piper_installed:
                # Fallback: Use espeak or simple placeholder
                logger.warning("Piper binary not found, using fallback TTS")
                return await self._fallback_tts(text)

            # Run piper to generate speech
            process = subprocess.Popen(
                [
                    'piper',
                    '--model', self.model_path,
                    '--output-raw'  # Output raw PCM data
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Send text and get audio
            stdout, stderr = process.communicate(input=text.encode('utf-8'), timeout=30)

            if process.returncode != 0:
                logger.error(f"Piper failed: {stderr.decode()}")
                return await self._fallback_tts(text)

            # Convert raw PCM to WAV format
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # 22.05 kHz sample rate
                wav_file.writeframes(stdout)

            wav_buffer.seek(0)
            return wav_buffer.read()

        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timed out")
            return await self._fallback_tts(text)
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise Exception(f"Failed to synthesize speech: {str(e)}")

    async def _fallback_tts(self, text: str) -> bytes:
        """
        Fallback TTS using system espeak (if available)

        Args:
            text: Text to synthesize

        Returns:
            WAV audio bytes
        """
        logger.info("Using espeak fallback for TTS")
        try:
            # Try espeak as fallback
            process = subprocess.run(
                ['espeak', '--stdout', text],
                capture_output=True,
                timeout=10,
                check=True
            )
            return process.stdout
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # If espeak also fails, return silent audio
            logger.warning("No TTS available, returning silent audio")
            return self._generate_silent_wav(2.0)  # 2 seconds of silence

    def _generate_silent_wav(self, duration: float) -> bytes:
        """
        Generate silent WAV file as placeholder

        Args:
            duration: Duration in seconds

        Returns:
            WAV audio bytes
        """
        sample_rate = 22050
        num_samples = int(sample_rate * duration)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            # Write silent frames (zeros)
            wav_file.writeframes(b'\x00\x00' * num_samples)

        wav_buffer.seek(0)
        return wav_buffer.read()


# Global service instance
piper_service = PiperService()
