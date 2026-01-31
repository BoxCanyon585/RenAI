from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama2"

    # Model Parameters
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Frontend
    frontend_path: str = "./frontend"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
