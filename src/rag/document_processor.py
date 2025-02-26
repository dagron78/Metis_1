# src/rag/document_processor.py
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
import time
import hashlib
import os

from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredFileLoader,
    TextLoader,
    PDFMinerLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.core.exceptions import DocumentProcessingError

# Configure logging
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document loading and preprocessing for RAG applications."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        supported_formats: Optional[List[str]] = None
    ):
        """
        Initialize the document processor.

        Args:
            chunk_size: Size of text chunks.
            chunk_overlap: Overlap between chunks.
            supported_formats: List of supported file extensions.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = supported_formats or ['.txt', '.pdf', '.docx']

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            is_separator_regex=False
        )

        self.loader_map = {
            '.txt': TextLoader,
            '.pdf': PDFMinerLoader,
            '.docx': UnstructuredFileLoader,
        }
        
        logger.info(f"Initialized DocumentProcessor with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        logger.info(f"Supported formats: {self.supported_formats}")

    def _validate_file(self, file_path: Path) -> bool:
        """Validates if a file is supported and exists."""
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False

        if file_path.suffix.lower() not in self.supported_formats:
            logger.warning(f"Unsupported file format: {file_path.suffix}")
            return False

        return True

    def _get_loader_for_file(self, file_path: Path) -> Optional[Any]:
        """Gets the appropriate loader for a file type."""
        return self.loader_map.get(file_path.suffix.lower())

    def _extract_section_info(self, text: str) -> Dict[str, Any]:
        """Extracts section information from text."""
        section_info = {
            "heading_level": 0,
            "section_name": "",
            "is_section_start": False
        }
        lines = text.split('\n')
        for line in lines[:2]:
            if line.startswith('#'):
                section_info["heading_level"] = line.count('#')
                section_info["section_name"] = line.strip('# ')
                section_info["is_section_start"] = True
                break
        return section_info

    def process_single_document(self, file_path: str) -> List[Document]:
        """Processes a single document file."""
        file_path = Path(file_path)
        logger.info(f"Entering process_single_document: {file_path}") # ADD THIS
        try:
            if not self._validate_file(file_path):
                raise ValueError(f"Invalid file: {file_path}")

            loader_class = self._get_loader_for_file(file_path)
            if not loader_class:
                raise ValueError(f"No loader available for: {file_path}")

            logger.info(f"Using loader: {loader_class.__name__}") # ADD THIS
            loader = loader_class(str(file_path))
            logger.info(f"About to call loader.load() for: {file_path}") # ADD THIS
            documents = loader.load()
            logger.info(f"loader.load() returned: {len(documents)} documents") # ADD THIS

            processed_chunks = []
            chunk_index = 0

            # Generate a unique document ID using a hash for better uniqueness
            doc_id = hashlib.sha256(f"{file_path}{time.time()}".encode()).hexdigest()
            logger.info(f"Generated doc_id: {doc_id} for document: {file_path}") # ADD THIS

            for doc in documents:
                doc.metadata.update({
                    "source": str(file_path),
                    "file_type": file_path.suffix,
                    "file_name": file_path.name,
                    "doc_id": doc_id,  # Add the unique document ID
                    "processed_at": datetime.now().isoformat()
                })

                chunks = self.text_splitter.split_documents([doc])
                logger.info(f"Split into {len(chunks)} chunks") # ADD THIS

                for chunk in chunks:
                    section_info = self._extract_section_info(chunk.page_content)
                    chunk.metadata.update({
                        "doc_id": doc_id,  # Add doc_id to each chunk
                        "chunk_index": chunk_index,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk.page_content),
                        "section_info": section_info,
                        "is_section_start": section_info["is_section_start"]
                    })
                    processed_chunks.append(chunk)
                    chunk_index += 1

            logger.info(f"Processed {file_path}: {len(processed_chunks)} chunks created, doc_id: {doc_id}")
            return processed_chunks

        except DocumentProcessingError as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing document {file_path}: {e}", exc_info=True)
            raise DocumentProcessingError(f"Failed to process document {file_path}: {str(e)}")

    def process_directory(self, directory_path: str) -> List[Document]:
        """Processes all supported documents in a directory."""
        directory_path = Path(directory_path)
        if not directory_path.is_dir():
            raise DocumentProcessingError(f"Invalid directory path: {directory_path}")

        logger.info(f"Processing directory: {directory_path}")
        all_chunks = []
        processed_files = 0
        failed_files = 0
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    chunks = self.process_single_document(str(file_path))
                    all_chunks.extend(chunks)
                    processed_files += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    failed_files += 1
                    continue  # Continue processing other files

        logger.info(f"Processed directory {directory_path}: {len(all_chunks)} total chunks created")
        logger.info(f"Successfully processed {processed_files} files, failed to process {failed_files} files")
        return all_chunks

    def get_document_metadata(self, chunks: List[Document]) -> Dict[str, Any]:
        """Gets metadata about processed documents."""
        unique_sources = set(chunk.metadata.get("source") for chunk in chunks)
        unique_doc_ids = set(chunk.metadata.get("doc_id") for chunk in chunks)
        
        stats = {
            "total_chunks": len(chunks),
            "unique_sources": len(unique_sources),
            "unique_documents": len(unique_doc_ids),
            "avg_chunk_size": sum(len(chunk.page_content) for chunk in chunks) / len(chunks) if chunks else 0,
            "sources": list(unique_sources),
            "chunk_size_distribution": {
                "min": min(len(chunk.page_content) for chunk in chunks) if chunks else 0,
                "max": max(len(chunk.page_content) for chunk in chunks) if chunks else 0
            },
            "section_starts": sum(1 for chunk in chunks if chunk.metadata.get("is_section_start", False))
        }
        return stats