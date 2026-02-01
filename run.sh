#!/bin/bash
# RenAI Desktop - Development Runner

set -e

echo "🚀 Starting RenAI Desktop Application"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal dependencies if not present
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q fastapi uvicorn ollama pydantic pydantic-settings python-multipart
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running!"
    echo "   Please start Ollama: ollama serve"
    echo ""
fi

echo "✅ Dependencies ready"
echo ""
echo "Starting backend server on http://127.0.0.1:8000"
echo "Starting Tauri desktop app..."
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start backend in background
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start Tauri in development mode
cd src-tauri
source "$HOME/.cargo/env"
cargo tauri dev

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null || true
