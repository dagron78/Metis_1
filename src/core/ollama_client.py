# src/core/ollama_client.py
import httpx
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError, Field
from src.core.config import settings  # Import settings

logger = logging.getLogger(__name__)

class ModelInfo(BaseModel):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: Dict[str, Any] = Field(default_factory=dict)

class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama.base_url
        self.client = httpx.AsyncClient()
        logger.info(f"Initialized OllamaClient with base URL: {self.base_url}")

    async def list_models(self) -> List[ModelInfo]:
        """Fetches available models from Ollama API."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [
                ModelInfo(
                    name=model.get("name", ""),
                    model=model.get("model", ""),
                    modified_at=model.get("modified_at", ""),
                    size=model.get("size", 0),
                    digest=model.get("digest", ""),
                    details=model.get("details", {}),
                )
                for model in data.get("models", [])
            ]
            logger.info(f"Retrieved {len(models)} models from Ollama")
            return models
        except httpx.RequestError as e:
            logger.error(f"Error fetching models from Ollama: {e}", exc_info=True)
            raise
        except ValidationError as e:
            logger.error(f"Error parsing Ollama response: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            raise

    async def close(self):
        await self.client.aclose()
        logger.info("OllamaClient connection closed")