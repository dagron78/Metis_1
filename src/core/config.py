# src/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class OllamaSettings(BaseSettings):
    base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    default_model: str = Field("llama2", env="RAG_LLM_MODEL")
    default_embedding_model: str = Field("nomic-ai/nomic-embed-text-v1", env="RAG_EMBEDDING_MODEL")
    max_retries: int = Field(3, env="RAG_OLLAMA_MAX_RETRIES")
    retry_delay: int = Field(1, env="RAG_OLLAMA_RETRY_DELAY")

class AuthSettings(BaseSettings):
    enabled: bool = Field(False, env="AUTH_ENABLED")
    secret_key: str = Field("default-secret-key-change-in-production", env="AUTH_SECRET_KEY")
    token_expire_minutes: int = Field(60, env="AUTH_TOKEN_EXPIRE_MINUTES")
    username: str = Field("admin", env="AUTH_USERNAME")
    password: str = Field("password", env="AUTH_PASSWORD")
    hashed_password: Optional[str] = Field(None, env="AUTH_HASHED_PASSWORD")

class Settings(BaseSettings):
    ollama: OllamaSettings = OllamaSettings()
    auth: AuthSettings = AuthSettings()
    uploads_dir: str = Field("uploads", env="RAG_UPLOADS_DIR")
    chroma_db_path: str = Field("chroma_db", env="RAG_CHROMA_DB_PATH")
    chat_histories_dir: str = Field("chat_histories", env="RAG_CHAT_HISTORIES_DIR")
    api_host: str = Field("0.0.0.0", env="RAG_API_HOST")
    api_port: int = Field(8002, env="RAG_API_PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")

settings = Settings()