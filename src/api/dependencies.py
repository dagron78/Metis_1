# src/api/dependencies.py
from fastapi import Depends, Security
from src.core.text_generation import TextGenerationService
from src.core.ollama_client import OllamaClient
from src.core.config import settings
from src.api.models.auth import get_current_active_user, User
from src.rag.vector_store import VectorStoreManager

async def get_ollama_client() -> OllamaClient:
    client = OllamaClient()
    try:
        yield client
    finally:
        await client.close()

async def get_text_gen_service(
    ollama_client: OllamaClient = Depends(get_ollama_client)
) -> TextGenerationService:
    return TextGenerationService(ollama_client)

def get_auth_dependency():
    """Returns the appropriate dependency based on whether auth is enabled."""
    if settings.auth.enabled:
        return Security(get_current_active_user)
    return None

# Add the get_vector_store function
def get_vector_store() -> VectorStoreManager:
    """Get the vector store manager."""
    from src.main import app
    return app.state.vector_store

async def get_current_user_optional(token: str = None) -> User:
    """Get current user if authenticated, otherwise return None."""
    if not settings.auth.enabled:
        # If auth is disabled, return a default user
        return User(username="Guest", disabled=False)
    
    if not token:
        return None
    
    try:
        from src.api.models.auth import get_current_user
        user = await get_current_user(token)
        return user
    except:
        return None