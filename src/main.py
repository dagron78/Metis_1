# src/main.py
import sys
print(f"Running main.py from: {__file__}")
print(f"Python path: {sys.path}")

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, Security
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.core.config import settings
from src.core.logging_config import setup_logging
from src.rag.document_processor import DocumentProcessor
from src.rag.vector_store import VectorStoreManager
from src.rag.query_engine import RAGQueryEngine
from src.api.routers import system, auth, web
from src.api.error_handlers import register_exception_handlers
from src.core.ollama_client import OllamaClient
from src.core.text_generation import TextGenerationService
from src.api.dependencies import get_ollama_client, get_text_gen_service, get_auth_dependency
from src.api.models.requests import QueryRequest
from src.api.models.responses import QueryResponse, DocumentListResponse, DocumentUploadResponse
from src.core.exceptions import DocumentProcessingError, QueryError

# Setup logging
setup_logging()

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Metis RAG API",
    description="REST API for RAG-based document query system with authentication and model selection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# --- Use settings for paths, and make them ABSOLUTE ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # /home/cqhoward/Metis_1
UPLOAD_DIR = PROJECT_ROOT / settings.uploads_dir
VECTOR_STORE_DIR = PROJECT_ROOT / settings.chroma_db_path
CHAT_HISTORY_DIR = PROJECT_ROOT / settings.chat_histories_dir

# Ensure directories exist
for directory in [UPLOAD_DIR, VECTOR_STORE_DIR, CHAT_HISTORY_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- Dependency Injection Setup ---
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Starting application...")
    app.state.ollama_client = OllamaClient()
    app.state.text_generation_service = TextGenerationService(
        ollama_client=app.state.ollama_client
    )
    app.state.document_processor = DocumentProcessor()
    app.state.vector_store = VectorStoreManager(persist_directory=str(VECTOR_STORE_DIR))
    app.state.query_engine = RAGQueryEngine(
        vector_store=app.state.vector_store,
        text_generation_service=app.state.text_generation_service
    )
    logger.info("Initialized application components")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")
    await app.state.ollama_client.close()
    logger.info("Closed OllamaClient connection")

# Dependencies for endpoints
def get_document_processor() -> DocumentProcessor:
    return app.state.document_processor

def get_vector_store() -> VectorStoreManager:
    return app.state.vector_store

def get_query_engine() -> RAGQueryEngine:
    return app.state.query_engine

# --- Include Routers ---
app.include_router(system.router, prefix="/system", tags=["System"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Include web router with a prefix to avoid conflicts with API endpoints
app.include_router(web.router, prefix="/ui", tags=["Web UI"])

# Fix: Use the dependency directly without calling it
auth_dependency = get_auth_dependency()

# --- API Endpoints ---
@app.post("/upload", response_model=DocumentUploadResponse, dependencies=[Depends(auth_dependency)] if auth_dependency else [])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload and process documents for RAG."""
    try:
        document_ids = []
        for file in files:
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            document_ids.append(str(file_path))
            # CORRECT: Pass only the function name and the file_path
            background_tasks.add_task(process_document, str(file_path))

        logger.info(f"Uploaded {len(files)} documents")
        return DocumentUploadResponse(
            message="Documents uploaded and queued for processing",
            num_processed=len(files),
            document_ids=document_ids
        )
    except Exception as e:
        logger.error(f"Error uploading documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# CORRECT: Use FastAPI's dependency injection within the background task
async def process_document(file_path: str):
    """Process a document and add it to the vector store."""
    document_processor = get_document_processor()  # Get instances directly
    vector_store = get_vector_store()             # Get instances directly
    try:
        logger.info(f"Starting to process document: {file_path}")
        chunks = document_processor.process_single_document(file_path)
        if not chunks:
            logger.warning(f"No chunks generated for document: {file_path}")
            return

        logger.info(f"Generated {len(chunks)} chunks from document: {file_path}")
        vector_store.add_documents(chunks)
        logger.info(f"Successfully processed and added document: {file_path}")

    except DocumentProcessingError as e:
        logger.error(f"Error processing document {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing document {file_path}: {e}", exc_info=True)

@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    query_engine: RAGQueryEngine = Depends(get_query_engine)
):
    """Query documents using RAG with optional model selection."""
    try:
        result = await query_engine.generate_response(
            query=request.query,
            chat_history_id=request.chat_history_id,
            filter_dict=request.filters,
            model_name=request.model_name,
            doc_id=request.doc_id
        )
        
        # Generate a unique ID if not provided
        chat_history_id = request.chat_history_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Processed query: '{request.query[:50]}...'")
        return QueryResponse(
            response=result, 
            sources=[], 
            chat_history_id=chat_history_id
        )
    except QueryError as e:
        logger.error(f"Error processing query: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", dependencies=[Depends(auth_dependency)] if auth_dependency else [])
async def get_stats(vector_store: VectorStoreManager = Depends(get_vector_store)):
    """Get statistics about the RAG system."""
    try:
        vector_store_stats = vector_store.get_collection_stats()
        return {
            "vector_store_stats": vector_store_stats,
            "uploaded_documents": len(list(UPLOAD_DIR.glob("*"))),
            "chat_histories": len(list(CHAT_HISTORY_DIR.glob("*.json")))
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear", dependencies=[Depends(auth_dependency)] if auth_dependency else [])
async def clear_system(vector_store: VectorStoreManager = Depends(get_vector_store)):
    """Clear all documents and reset the system."""
    try:
        vector_store.clear_collection()
        for file in UPLOAD_DIR.glob("*"):
            file.unlink()
        for file in CHAT_HISTORY_DIR.glob("*.json"):
            file.unlink()
        logger.info("System cleared successfully")
        return {"message": "System cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing system: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(vector_store: VectorStoreManager = Depends(get_vector_store)):
    """List all documents in the system."""
    try:
        documents = vector_store.list_documents()
        total_documents = len(documents)
        total_chunks = sum(doc['chunk_count'] for doc in documents)
        logger.info(f"Listed {total_documents} documents with {total_chunks} total chunks")
        return DocumentListResponse(
            documents=documents,
            total_documents=total_documents,
            total_chunks=total_chunks
        )
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )