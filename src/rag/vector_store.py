# src/rag/vector_store.py
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import shutil
import os
import time

from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings  # Changed back to SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from src.core.config import settings
from src.core.exceptions import VectorStoreError

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages vector storage and retrieval operations for RAG applications."""

    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "rag_documents",
        distance_metric: str = "cosine"
    ):
        """
        Initialize the vector store manager.

        Args:
            persist_directory: Directory to persist vector store.
            collection_name: Name of the Chroma collection.
            distance_metric: Metric for similarity search.
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        self._initialize_embeddings()
        self._initialize_vector_store()
        logger.info(f"Initialized VectorStoreManager with persist_directory={persist_directory}, collection_name={collection_name}")

    def _initialize_embeddings(self):
        """Initialize embedding function with Sentence Transformers."""
        try:
            self.embedding_function = SentenceTransformerEmbeddings(
                model_name=settings.ollama.default_embedding_model,
                model_kwargs={"trust_remote_code": True}  # ADD THIS
            )
            logger.info(f"Initialized embedding model: {settings.ollama.default_embedding_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to initialize embedding model: {str(e)}")

    def _initialize_vector_store(self):
        """Initialize or load existing vector store."""
        try:
            if self.persist_directory.exists():
                self.vector_store = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embedding_function,
                    collection_name=self.collection_name
                )
                logger.info(f"Loaded existing vector store from {self.persist_directory}")
            else:
                self.persist_directory.mkdir(parents=True, exist_ok=True)
                self.vector_store = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embedding_function,
                    collection_name=self.collection_name
                )
                logger.info(f"Created new vector store at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to initialize vector store: {str(e)}")

    def add_documents(self, documents: List[Document], batch_size: int = 100) -> None:
        """Adds documents to the vector store, handling metadata."""
        logger.info(f"Entering add_documents: {len(documents)} documents") # ADD THIS
        if not documents:
            logger.warning("No documents provided to add_documents")
            return

        try:
            filtered_documents = []
            for doc in documents:
                filtered_metadata = {}
                for key, value in doc.metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        filtered_metadata[key] = value
                    elif value is None:
                        filtered_metadata[key] = value
                    else:
                        try:
                            filtered_metadata[key] = str(value)
                        except Exception:
                            logger.warning(f"Skipping complex metadata field: {key}")

                filtered_doc = Document(
                    page_content=doc.page_content,
                    metadata=filtered_metadata
                )
                filtered_documents.append(filtered_doc)

            total_batches = (len(filtered_documents) + batch_size - 1) // batch_size
            logger.info(f"Adding {len(filtered_documents)} documents in {total_batches} batches")

            for i in range(0, len(filtered_documents), batch_size):
                batch = filtered_documents[i:i + batch_size]
                logger.info(f"About to call self.vector_store.add_documents for batch {i // batch_size + 1}") # ADD THIS
                self.vector_store.add_documents(batch)
                logger.info(f"self.vector_store.add_documents returned for batch {i // batch_size + 1}") # ADD THIS
                logger.info(f"Added batch of {len(batch)} documents to vector store")

            logger.info(f"Successfully added {len(documents)} documents to vector store")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to add documents to vector store: {str(e)}")

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Performs similarity search."""
        try:
            # Only use $and if there are multiple conditions
            where = filter_dict
            logger.info(f"Performing similarity search for query: '{query[:50]}...' with k={k}, filter={where}")
            
            documents = self.vector_store.similarity_search(
                query,
                k=k,
                filter=where
            )
            
            logger.info(f"Found {len(documents)} documents for query")
            return documents
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to perform similarity search: {str(e)}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Gets statistics about the vector store collection."""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            stats = {
                "total_documents": count,  # This is actually total *chunks*
                "persist_directory": str(self.persist_directory),
                "collection_name": self.collection_name,
                "embedding_model": settings.ollama.default_embedding_model
            }
            logger.info(f"Retrieved collection stats: {count} total documents")
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to get collection stats: {str(e)}")

    def clear_collection(self) -> None:
        """Clears all documents from the vector store."""
        try:
            logger.warning("Clearing vector store collection")
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
            self._initialize_vector_store()
            logger.info("Successfully cleared vector store collection")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to clear vector store: {str(e)}")

    def list_documents(self) -> List[Dict[str, Any]]:
        """Gets a list of all documents in the vector store with metadata."""
        try:
            collection = self.vector_store._collection
            documents = collection.get()

            if not documents or not documents.get('documents'):
                logger.info("No documents found in vector store")
                return []

            doc_groups = {}
            for i, doc in enumerate(documents['documents']):
                metadata = documents['metadatas'][i]
                doc_id = metadata.get('doc_id', f"unknown_{i}")  # Use doc_id
                source = metadata.get('source', 'Unknown source')

                if doc_id not in doc_groups:
                    doc_groups[doc_id] = {
                        'source': source,
                        'file_type': metadata.get('file_type', ''),
                        'file_name': metadata.get('file_name', ''),
                        'chunk_count': 1,
                        'added_at': metadata.get('processed_at', ''),  # Use processed_at
                        'doc_id': doc_id  # Include doc_id in the output
                    }
                else:
                    doc_groups[doc_id]['chunk_count'] += 1

            doc_list = list(doc_groups.values())
            doc_list.sort(key=lambda x: x['source'])  # Sort by source

            logger.info(f"Listed {len(doc_list)} documents from vector store")
            return doc_list

        except Exception as e:
            logger.error(f"Error listing documents: {e}", exc_info=True)
            raise VectorStoreError(f"Failed to list documents: {str(e)}")