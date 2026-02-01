import ollama
from typing import AsyncGenerator, List, Dict, Any
from backend.config import settings


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self):
        """Initialize Ollama async client."""
        self.client = ollama.AsyncClient(host=settings.ollama_base_url)

    async def generate_stream(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from Ollama.

        Args:
            prompt: User prompt to send to the model
            model: Model name (uses default if not specified)
            temperature: Sampling temperature (uses default if not specified)
            max_tokens: Maximum tokens to generate (uses default if not specified)

        Yields:
            Generated tokens as they arrive
        """
        model = model or settings.default_model
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens

        try:
            stream = await self.client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            async for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]

        except Exception as e:
            raise Exception(f"Error generating response from Ollama: {str(e)}")

    async def list_models(self) -> List[str]:
        """
        List available Ollama models.

        Returns:
            List of model names
        """
        try:
            response = await self.client.list()
            return [model["name"] for model in response.get("models", [])]
        except Exception as e:
            raise Exception(f"Error listing Ollama models: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if Ollama is accessible.

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            await self.client.list()
            return True
        except Exception:
            return False


# Global service instance
ollama_service = OllamaService()
