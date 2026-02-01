from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from backend.config import settings
from backend.routers import chat, health, stt, tts
from backend.services.ollama_service import ollama_service
from backend.services.whisper_service import whisper_service
from backend.services.piper_service import piper_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup: Check Ollama connection
    print("Starting RenAI...")
    print(f"Ollama URL: {settings.ollama_base_url}")

    is_connected = await ollama_service.health_check()
    if is_connected:
        print("✓ Ollama is connected")
        try:
            models = await ollama_service.list_models()
            print(f"✓ Available models: {', '.join(models)}")
        except Exception as e:
            print(f"⚠ Warning: Could not list models: {e}")
    else:
        print("⚠ Warning: Ollama is not connected. Please ensure Ollama is running.")

    # Initialize speech services (lazy loading)
    print("✓ Speech services ready (models will load on first use)")

    yield

    # Shutdown
    print("Shutting down RenAI...")


# Create FastAPI app
app = FastAPI(
    title="RenAI",
    description="Fast & Responsive AI Assistant for Home Network",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(stt.router)
app.include_router(tts.router)

# Mount static files and frontend
frontend_path = Path(settings.frontend_path)
if frontend_path.exists():
    # Serve static files (CSS, JS)
    static_path = frontend_path / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Serve index.html at root
    @app.get("/")
    async def read_root():
        """Serve the frontend index.html."""
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "RenAI API is running. Frontend not found."}
else:
    @app.get("/")
    async def read_root():
        """API root endpoint when frontend is not available."""
        return {
            "message": "RenAI API is running",
            "version": "1.0.0",
            "docs": "/docs",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
