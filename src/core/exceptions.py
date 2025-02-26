# src/core/exceptions.py

class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    pass

class ModelError(BaseAppException):
    """Base exception for model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Raised when specified model is not available."""
    pass

class ModelSwitchError(ModelError):
    """Raised when model switch operation fails."""
    pass

class DocumentProcessingError(BaseAppException):
    """Raised when document processing fails."""
    pass

class VectorStoreError(BaseAppException):
    """Base exception for vector store related errors."""
    pass

class QueryError(BaseAppException):
    """Raised when query processing fails."""
    pass

class AuthenticationError(BaseAppException):
    """Raised for authentication related errors."""
    pass