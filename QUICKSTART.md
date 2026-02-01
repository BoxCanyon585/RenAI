# RenAI Desktop - Quick Start Guide

## 🚀 Development Setup (Simplified)

Since `faster-whisper` has complex dependencies, here's a simplified approach to get started:

### Option 1: Run Without Speech Features (Fastest)

1. **Install Core Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn ollama pydantic pydantic-settings python-multipart
   ```

2. **Start Backend**
   ```bash
   source venv/bin/activate
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **In Another Terminal - Start Tauri**
   ```bash
   source "$HOME/.cargo/env"
   cd src-tauri
   cargo tauri dev
   ```

### Option 2: Full Installation with Speech (Python 3.10+ Required)

If you want speech features, you need Python 3.10 or higher:

1. **Install Python 3.11+ via Homebrew**
   ```bash
   brew install python@3.11
   ```

2. **Create Virtual Environment with Python 3.11**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install All Dependencies**
   ```bash
   pip install --upgrade pip
   pip install fastapi uvicorn ollama pydantic pydantic-settings python-multipart
   pip install faster-whisper soundfile numpy
   # piper-tts requires Python 3.10+
   pip install piper-tts
   ```

4. **Download Speech Models**
   ```bash
   python scripts/download_models.py
   ```

5. **Start Backend**
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

6. **In Another Terminal - Start Tauri**
   ```bash
   source "$HOME/.cargo/env"
   cd src-tauri
   cargo tauri dev
   ```

## 📦 Building Production Binaries

### Prerequisites
- Backend Python dependencies installed
- Ollama running locally

### Build Commands

#### macOS (DMG)
```bash
source venv/bin/activate
cd src-tauri
cargo tauri build --target universal-apple-darwin
```

Output: `src-tauri/target/release/bundle/dmg/RenAI_2.0.0_universal.dmg`

#### Windows (MSI) - Cross-compile or build on Windows
```bash
# On Windows with Rust installed:
cargo tauri build --target x86_64-pc-windows-msvc
```

Output: `src-tauri/target/release/bundle/msi/RenAI_2.0.0_x64.msi`

#### Linux (AppImage/DEB)
```bash
# On Linux:
cargo tauri build
```

Outputs:
- `src-tauri/target/release/bundle/appimage/RenAI_2.0.0_amd64.AppImage`
- `src-tauri/target/release/bundle/deb/renai_2.0.0_amd64.deb`

### Build Notes

**Important**: The current implementation expects the backend to be run as a subprocess. For production distribution, you'll need to:

1. **Bundle Python with the app** (use PyInstaller or similar)
2. **Or include Python installation** as a prerequisite
3. **Or use the backend as a separate service**

## 🎯 Features Status

| Feature | Status | Notes |
|---------|--------|-------|
| Chat with Ollama | ✅ Working | Requires Ollama running |
| System Tray | ✅ Working | Show/Hide/Quit |
| Window Management | ✅ Working | Close → minimize to tray |
| Microphone Button | ✅ UI Ready | Requires Python 3.10+ for full functionality |
| Speech-to-Text | ⚠️ Partial | Needs faster-whisper installed |
| Text-to-Speech | ⚠️ Partial | Fallback to silent audio |
| Settings Panel | ✅ Working | Auto-TTS toggle, model selection |

## 🐛 Troubleshooting

### "Module not found" errors
- Make sure you activated the virtual environment: `source venv/bin/activate`

### Backend won't start
- Check Ollama is running: `ollama serve`
- Verify port 8000 is not in use: `lsof -i :8000`

### Tauri build fails
- Update Rust: `rustup update`
- Clear build cache: `cargo clean` in `src-tauri/`

### Speech features not working
- Check Python version: `python --version` (needs 3.10+)
- Install system dependencies: `brew install pkg-config ffmpeg`
- Reinstall faster-whisper: `pip install --no-cache-dir faster-whisper`

## 📝 Next Steps

1. Get Ollama running: `ollama serve`
2. Pull a model: `ollama pull llama2`
3. Start the app using Option 1 above
4. Test chat functionality
5. (Optional) Upgrade to Python 3.11 for speech features

