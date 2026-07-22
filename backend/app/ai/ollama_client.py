"""
Ollama client: async wrapper around the Ollama REST API for text generation
and streaming responses.
"""
import json
from typing import AsyncGenerator

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Async client for the Ollama local LLM API."""

    def __init__(self):
        self.base_url = settings.ollama_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout

    async def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                data = resp.json()
                model_names = [m.get("name", "") for m in data.get("models", [])]
                # Check for exact match or version-less match
                for name in model_names:
                    if self.model in name or name.startswith(self.model.split(":")[0]):
                        return True
                logger.warning(
                    f"Model '{self.model}' not found. Available: {model_names}. "
                    f"Run: ollama pull {self.model}"
                )
                return False
        except Exception as e:
            logger.warning(f"Ollama not reachable: {e}")
            return False

    async def generate(self, prompt: str, system: str = "") -> str:
        """
        Generate a single (non-streaming) response.
        Returns the full response text.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 2048,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except httpx.TimeoutException:
            raise RuntimeError("Ollama request timed out. Try a smaller model or increase OLLAMA_TIMEOUT.")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}") from e

    async def generate_stream(
        self, prompt: str, system: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Stream tokens from Ollama one chunk at a time.
        Yields text fragments as they arrive.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.4,
                "num_predict": 4096,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                yield token
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException:
            yield "\n\n⚠️ Response timed out. The model may be too large for your hardware."
        except Exception as e:
            yield f"\n\n❌ Error: {str(e)}"


# Singleton instance
ollama = OllamaClient()
