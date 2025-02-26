# src/rag/query_engine.py
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from .vector_store import VectorStoreManager
from src.core.text_generation import TextGenerationService
from src.core.config import settings
from src.core.exceptions import QueryError
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = logging.getLogger(__name__)

class RAGQueryEngine:
    def __init__(self, vector_store: VectorStoreManager, text_generation_service: TextGenerationService):
        self.vector_store = vector_store
        self.text_generation_service = text_generation_service
        self._initialize_prompt_template()
        self.chat_histories_dir = Path(settings.chat_histories_dir)
        self.chat_histories_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized RAGQueryEngine with TextGenerationService")

    def _initialize_prompt_template(self):
        """Initializes the chat prompt template."""
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant that answers questions based on the provided context. "
                       "If the context doesn't contain relevant information, say you don't know. "
                       "Always cite your sources by referring to the document names."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "Context:\n{context}\n\nQuestion:\n{question}")
        ])
        logger.info("Initialized prompt template")

    async def generate_response(
        self,
        query: str,
        chat_history_id: Optional[str] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        k_documents: int = 6,
        model_name: Optional[str] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """Generates a response using RAG with optional model selection."""
        try:
            # --- Combine filter_dict and doc_id filter ---
            final_filter = {}
            if filter_dict:
                final_filter.update(filter_dict)
            if doc_id:
                final_filter["doc_id"] = doc_id

            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(
                query,
                k=k_documents,
                filter_dict=final_filter if final_filter else None
            )

            if not relevant_docs:
                logger.warning(f"No relevant documents found for query: {query}")
                return "I couldn't find any relevant information to answer your question."

            # Format the context
            context = self._format_context(relevant_docs)
            
            # Load chat history if provided
            history_messages = []
            if chat_history_id:
                history_messages = self._load_chat_history(chat_history_id)
            elif chat_history:
                history_messages = chat_history

            # Format the prompt
            formatted_prompt = self.prompt_template.format_messages(
                context=context,
                question=query,
                chat_history=history_messages
            )

            # Generate the response using the TextGenerationService
            # Use the current model if none is specified
            response = await self.text_generation_service.generate_text(
                prompt=formatted_prompt,
                model_name=model_name or self.text_generation_service.current_model
            )

            # Save chat history if chat_history_id is provided
            if chat_history_id:
                self._save_chat_history(
                    chat_history_id,
                    query,
                    response,
                    history_messages
                )

            logger.info(f"Generated response using model: {model_name or self.text_generation_service.current_model}")
            return response

        except Exception as e:
            logger.error(f"Error in generate_response: {e}", exc_info=True)
            raise QueryError(f"Failed to generate response: {str(e)}")

    def _format_context(self, documents: List[Any]) -> str:
        """Formats the retrieved documents into a context string."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown source")
            file_name = doc.metadata.get("file_name", "Unknown file")
            context_parts.append(f"[Document {i} from {file_name}]\n{doc.page_content}")
        
        return "\n\n".join(context_parts)

    def _extract_sources(self, documents: List[Any]) -> List[str]:
        """Extracts source information from documents."""
        sources = []
        for doc in documents:
            source = doc.metadata.get("source", "Unknown source")
            if source not in sources:
                sources.append(source)
        return sources

    def _load_chat_history(self, chat_history_id: str) -> List[Dict[str, Any]]:
        """Loads chat history from file."""
        try:
            history_file = self.chat_histories_dir / f"{chat_history_id}.json"
            if not history_file.exists():
                logger.info(f"No chat history found for ID: {chat_history_id}")
                return []
            
            with open(history_file, 'r') as f:
                history_data = json.load(f)
            
            # Convert to format expected by prompt template
            messages = []
            for entry in history_data:
                if entry["role"] == "user":
                    messages.append(("user", entry["content"]))
                elif entry["role"] == "assistant":
                    messages.append(("assistant", entry["content"]))
            
            logger.info(f"Loaded chat history for ID: {chat_history_id}, {len(messages)} messages")
            return messages
        except Exception as e:
            logger.error(f"Error loading chat history: {e}", exc_info=True)
            return []

    def _save_chat_history(
        self,
        chat_history_id: str,
        query: str,
        response: str,
        previous_history: List[Dict[str, Any]]
    ) -> None:
        """Saves chat history to file."""
        try:
            history_file = self.chat_histories_dir / f"{chat_history_id}.json"
            
            # Convert previous history to serializable format
            history_data = []
            for entry in previous_history:
                if isinstance(entry, tuple) and len(entry) == 2:
                    role, content = entry
                    history_data.append({"role": role, "content": content})
                elif isinstance(entry, dict) and "role" in entry and "content" in entry:
                    history_data.append(entry)
            
            # Add new messages
            history_data.append({"role": "user", "content": query})
            history_data.append({"role": "assistant", "content": response})
            
            # Save to file
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            logger.info(f"Saved chat history for ID: {chat_history_id}")
        except Exception as e:
            logger.error(f"Error saving chat history: {e}", exc_info=True)