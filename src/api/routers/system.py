# src/api/routers/system.py
from fastapi import APIRouter, HTTPException, Depends, Security
from typing import List, Dict
import logging
from src.core.ollama_client import OllamaClient, ModelInfo
from src.core.text_generation import TextGenerationService
from src.api.dependencies import get_ollama_client, get_text_gen_service, get_auth_dependency
from src.core.exceptions import ModelNotFoundError
from src.api.models.responses import ModelListResponse, ModelSwitchResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/models", response_model=ModelListResponse)
async def list_models(ollama_client: OllamaClient = Depends(get_ollama_client)):
    """Lists available models from Ollama."""
    try:
        models = await ollama_client.list_models()
        logger.info(f"Listed {len(models)} models")
        return ModelListResponse(models=models)
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Fix: Use the dependency directly without calling it
auth_dependency = get_auth_dependency()
@router.post("/models/{model_name}", response_model=ModelSwitchResponse, dependencies=[Depends(auth_dependency)] if auth_dependency else [])
async def switch_model(model_name: str, text_gen: TextGenerationService = Depends(get_text_gen_service)) -> Dict[str, str]:
    """Switches to the specified model."""
    try:
        await text_gen.set_model(model_name)
        logger.info(f"Switched to model: {model_name}")
        return ModelSwitchResponse(current_model=model_name)
    except ModelNotFoundError:
        logger.warning(f"Model not found: {model_name}")
        raise
    except Exception as e:
        logger.error(f"Error switching model: {e}", exc_info=True)
        raise

@router.get("/models/current", response_model=Dict[str, str])
async def get_current_model(text_gen: TextGenerationService = Depends(get_text_gen_service)) -> Dict[str, str]:
    """Returns the currently selected model."""
    return {"current_model": text_gen.current_model}

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@router.get("/info")
async def system_info():
    """System information endpoint."""
    import platform
    import sys
    
    return {
        "system": {
            "os": platform.system(),
            "python_version": sys.version,
            "platform": platform.platform()
        },
        "app": {
            "auth_enabled": auth_dependency is not None
        }
    }