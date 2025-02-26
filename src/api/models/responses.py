# src/api/models/responses.py
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.core.ollama_client import ModelInfo

class QueryResponse(BaseModel):
    response: str = Field(..., description="The generated response")
    sources: List[str] = Field(..., description="Sources used in generating the response")
    chat_history_id: str = Field(..., description="ID of the chat history")

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

class ModelSwitchResponse(BaseModel):
    status: str = Field("success", description="Status of the model switch operation")
    current_model: str = Field(..., description="The currently active model")

class DocumentUploadResponse(BaseModel):
    message: str
    num_processed: int
    document_ids: List[str]

class DocumentInfo(BaseModel):
    source: str = Field(..., description="Original document path")
    file_type: str = Field(..., description="Document type/extension")
    file_name: str = Field(..., description="Original file name")
    chunk_count: int = Field(..., description="Number of chunks from this document")
    added_at: str = Field(..., description="Timestamp when document was added")
    doc_id: str = Field(..., description="Unique document ID")

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total_documents: int = Field(..., description="Total number of unique documents")
    total_chunks: int = Field(..., description="Total number of chunks across all documents")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    error_type: str = Field(..., description="Type of error")