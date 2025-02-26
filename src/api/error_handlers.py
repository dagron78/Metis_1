# src/api/error_handlers.py
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from src.core.exceptions import (
    BaseAppException,
    ModelError,
    ModelNotFoundError,
    ModelSwitchError,
    DocumentProcessingError,
    VectorStoreError,
    QueryError,
    AuthenticationError
)

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    """Register custom exception handlers for the application."""
    
    @app.exception_handler(ModelNotFoundError)
    async def model_not_found_exception_handler(request: Request, exc: ModelNotFoundError):
        logger.warning(f"Model not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_404_NOT_FOUND,
                "error_type": "ModelNotFoundError"
            },
        )
    
    @app.exception_handler(ModelSwitchError)
    async def model_switch_exception_handler(request: Request, exc: ModelSwitchError):
        logger.error(f"Model switch error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": "ModelSwitchError"
            },
        )
    
    @app.exception_handler(ModelError)
    async def model_exception_handler(request: Request, exc: ModelError):
        logger.error(f"Model error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": "ModelError"
            },
        )
    
    @app.exception_handler(DocumentProcessingError)
    async def document_processing_exception_handler(request: Request, exc: DocumentProcessingError):
        logger.error(f"Document processing error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
                "error_type": "DocumentProcessingError"
            },
        )
    
    @app.exception_handler(VectorStoreError)
    async def vector_store_exception_handler(request: Request, exc: VectorStoreError):
        logger.error(f"Vector store error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": "VectorStoreError"
            },
        )
    
    @app.exception_handler(QueryError)
    async def query_exception_handler(request: Request, exc: QueryError):
        logger.error(f"Query error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
                "error_type": "QueryError"
            },
        )
    
    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "error_type": "AuthenticationError"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        logger.error(f"Application error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": exc.__class__.__name__
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred. Please check the logs for details.",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": "UnhandledException"
            },
        )