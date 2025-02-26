# src/core/text_generation.py
from langchain_ollama import OllamaLLM
import logging
from typing import Optional, List
from .ollama_client import OllamaClient
from .config import settings
from .exceptions import ModelNotFoundError

logger = logging.getLogger(__name__)

class TextGenerationService:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.current_model = settings.ollama.default_model
        self._initialize_llm()
        logger.info(f"Initialized TextGenerationService with model: {self.current_model}")

    def _initialize_llm(self, model_name: Optional[str] = None):
        """Initializes or re-initializes the OllamaLLM object."""
        model_to_use = model_name or self.current_model
        try:
            self.llm = OllamaLLM(
                model=model_to_use,
                base_url=settings.ollama.base_url
            )
            logger.info(f"Initialized LLM with model: {model_to_use}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM with model {model_to_use}: {e}", exc_info=True)
            raise

    async def set_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        models = await self.ollama_client.list_models()
        if not any(m.name == model_name for m in models):
            logger.error(f"Model {model_name} not found in available models")
            raise ModelNotFoundError(f"Model {model_name} not available")

        try:
            self._initialize_llm(model_name=model_name)
            self.current_model = model_name
            logger.info(f"Successfully switched to model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to model {model_name}: {e}", exc_info=True)
            raise

    async def generate_text(self, prompt: List, model_name: Optional[str] = None) -> str:
        """Generate text using specified or current model."""
        if model_name and model_name != self.current_model:
            await self.set_model(model_name)

        try:
            response = self.llm.invoke(prompt)
            # Fix: Check if response is a string or an object with content attribute
            if isinstance(response, str):
                return response
            elif hasattr(response, 'content'):
                return response.content
            else:
                # If it's neither, convert it to a string
                return str(response)
        except Exception as e:
            logger.error(f"Error generating text with model {self.current_model}: {e}", exc_info=True)
            raise