# src/api/models/requests.py
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask", min_length=1)
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for retrieval")
    model_name: Optional[str] = Field(None, description="The model to use for generation")
    doc_id: Optional[str] = Field(None, description="Optional document ID to filter by")
    chat_history_id: Optional[str] = Field(None, description="Optional chat history ID for context")

class ModelSwitchRequest(BaseModel):
    model_name: str = Field(..., description="The name of the model to switch to")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")