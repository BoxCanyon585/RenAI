import json
from typing import AsyncGenerator, Dict, Any


def format_sse(data: Dict[str, Any], event: str = None) -> str:
    """
    Format data as Server-Sent Event (SSE).

    Args:
        data: Data to send
        event: Optional event type

    Returns:
        Formatted SSE string
    """
    message = f"data: {json.dumps(data)}\n\n"
    if event:
        message = f"event: {event}\n{message}"
    return message


async def event_generator(
    ollama_stream: AsyncGenerator[str, None],
) -> AsyncGenerator[str, None]:
    """
    Convert Ollama stream to SSE format.

    Args:
        ollama_stream: Async generator from Ollama service

    Yields:
        SSE formatted events
    """
    try:
        async for token in ollama_stream:
            yield format_sse({"token": token}, event="token")

        # Send done event when stream completes
        yield format_sse({"done": True}, event="done")

    except Exception as e:
        # Send error event if something goes wrong
        yield format_sse({"error": str(e)}, event="error")
