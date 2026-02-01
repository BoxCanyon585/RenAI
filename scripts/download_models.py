#!/usr/bin/env python3
"""
Download speech models for RenAI
- Whisper: base.en model (~150MB)
- Piper TTS: en_US-lessac-medium voice (~30MB)
"""

import os
import sys
import urllib.request
from pathlib import Path


def download_file(url: str, dest_path: Path, description: str):
    """Download a file with progress indicator"""
    print(f"\nDownloading {description}...")
    print(f"URL: {url}")
    print(f"Destination: {dest_path}")

    # Create parent directory if it doesn't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if file already exists
    if dest_path.exists():
        print(f"✓ {description} already exists. Skipping.")
        return

    def reporthook(block_num, block_size, total_size):
        """Progress callback"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
        else:
            mb_downloaded = downloaded / (1024 * 1024)
            print(f"\r  Downloaded: {mb_downloaded:.1f} MB", end='')

    try:
        urllib.request.urlretrieve(url, dest_path, reporthook)
        print(f"\n✓ {description} downloaded successfully!")
    except Exception as e:
        print(f"\n✗ Failed to download {description}: {e}")
        if dest_path.exists():
            dest_path.unlink()  # Remove partial download
        raise


def download_whisper_model(model_size: str = "base.en"):
    """
    Download Whisper model from Hugging Face
    Note: faster-whisper will download the model automatically on first use,
    but this pre-downloads it for better first-run experience
    """
    print(f"\n{'='*60}")
    print(f"WHISPER MODEL: {model_size}")
    print(f"{'='*60}")

    # faster-whisper downloads models to cache directory
    # We'll let it handle the download on first use
    # This is just a placeholder for future manual download logic

    print(f"✓ Whisper {model_size} will be downloaded automatically on first use")
    print(f"  (faster-whisper handles model downloads internally)")
    print(f"  Model size: ~150MB")


def download_piper_model():
    """Download Piper TTS voice model"""
    print(f"\n{'='*60}")
    print("PIPER TTS MODEL")
    print(f"{'='*60}")

    models_dir = Path("models/piper")

    # Piper voice: en_US-lessac-medium
    # High-quality voice from Hugging Face
    voice_name = "en_US-lessac-medium"
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"

    # Download model file (.onnx)
    model_url = f"{base_url}/{voice_name}.onnx"
    model_path = models_dir / f"{voice_name}.onnx"
    download_file(model_url, model_path, f"Piper voice model ({voice_name}.onnx)")

    # Download config file (.json)
    config_url = f"{base_url}/{voice_name}.onnx.json"
    config_path = models_dir / f"{voice_name}.onnx.json"
    download_file(config_url, config_path, f"Piper voice config ({voice_name}.onnx.json)")


def main():
    """Main download function"""
    print("\n" + "="*60)
    print("RenAI Speech Models Downloader")
    print("="*60)

    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    print(f"\nProject root: {project_root}")

    try:
        # Download Whisper model (auto-download)
        download_whisper_model("base.en")

        # Download Piper TTS model
        download_piper_model()

        print("\n" + "="*60)
        print("✓ ALL MODELS READY!")
        print("="*60)
        print("\nYou can now use voice features in RenAI.")
        print("\nNotes:")
        print("  - Whisper model will download (~150MB) on first transcription")
        print("  - Piper TTS model is ready to use")
        print("  - Models are stored in: models/")

        return 0

    except KeyboardInterrupt:
        print("\n\n✗ Download cancelled by user")
        return 1
    except Exception as e:
        print(f"\n\n✗ Download failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
