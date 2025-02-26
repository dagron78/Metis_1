
# Metis RAG

Metis RAG is a Retrieval-Augmented Generation system that combines the power of large language models with your own documents. This allows you to get accurate, contextually relevant answers to your questions based on the content of your documents.

## Features

- **Document Processing**: Upload and process multiple document formats (PDF, TXT, DOCX)
- **Secure Authentication**: User authentication system with JWT tokens
- **Interactive Web UI**: User-friendly interface for document management and chat
- **Multiple Model Support**: Switch between different language models
- **Document-Specific Querying**: Ask questions about specific documents
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling with custom exceptions
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Hybrid Model Integration**: Uses Ollama for text generation and SentenceTransformers for embeddings

## Recent Improvements

- **SentenceTransformer Embeddings**: Using SentenceTransformerEmbeddings with the nomic-ai/nomic-embed-text-v1 model for high-quality embeddings
- **Proper Dependency Injection**: Implemented FastAPI's Depends mechanism correctly in background tasks for better testability and maintainability
- **Enhanced Response Handling**: Better handling of different response types from language models
- **Improved Error Handling**: More robust error handling and logging

## Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) for local language models
- Docker and Docker Compose (optional, for containerized deployment)

### Required Models

- **Ollama Models**:
  - `llama2` (or another model of your choice) - For text generation
  
  You can pull this model with:
  ```bash
  ollama pull llama2
  ```

- **Hugging Face Models**:
  - `nomic-ai/nomic-embed-text-v1` - For document embeddings (automatically downloaded when first used)
  
  This model requires the `einops` package:
  ```bash
  pip install einops
  ```

### Installation

#### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/metis-rag.git
   cd metis-rag
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   RAG_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1
   RAG_LLM_MODEL=llama2
   OLLAMA_BASE_URL=http://localhost:11434
   RAG_OLLAMA_MAX_RETRIES=3
   RAG_OLLAMA_RETRY_DELAY=1
   RAG_UPLOADS_DIR=uploads
   RAG_CHROMA_DB_PATH=chroma_db
   RAG_CHAT_HISTORIES_DIR=chat_histories
   RAG_API_HOST=0.0.0.0
   RAG_API_PORT=8002
   
   # Authentication settings
   AUTH_ENABLED=false  # Set to true to enable authentication
   AUTH_SECRET_KEY=your-secret-key-here-change-in-production
   AUTH_TOKEN_EXPIRE_MINUTES=60
   AUTH_USERNAME=admin
   AUTH_PASSWORD=securepassword
   
   # Logging settings
   LOG_LEVEL=INFO
   LOG_FILE=logs/app.log
   ```

5. Create required directories:
   ```bash
   mkdir -p uploads chroma_db chat_histories logs
   ```

6. Start the application:
   ```bash
   ./start.sh
   ```

7. Access the web interface at http://localhost:8002

#### Docker Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/metis-rag.git
   cd metis-rag
   ```

2. Start the containers:
   ```bash
   ./start_docker.sh
   ```

3. Access the web interface at http://localhost:8002

## Usage

### Uploading Documents

1. Navigate to the Documents page
2. Click the "Choose Files" button and select one or more documents
3. Click "Upload" to upload and process the documents

### Asking Questions

1. Navigate to the Chat page
2. Type your question in the input field
3. Click "Send" to get an answer based on your documents

### Switching Models

1. Use the model selector dropdown in the Chat page
2. Select a different model to switch to it

### Viewing Statistics

1. Navigate to the Stats page to view system statistics
2. See information about the vector store, uploaded documents, and chat histories

## Test Documents and API Script

### Test Documents

The repository includes sample test documents in the `Test_Docs` directory:

- `rag_overview.txt` - Information about RAG technology and its components
- `authentication_security.txt` - Information about authentication methods and security best practices

You can use these documents to test the system without having to create your own.

### API Testing Script

The repository includes a Python script `test_api.py` that demonstrates how to interact with the API programmatically:

```bash
# Upload test documents
./test_api.py upload Test_Docs/rag_overview.txt Test_Docs/authentication_security.txt

# List all documents
./test_api.py list

# Query the system
./test_api.py query "What is RAG?"

# Query a specific document
./test_api.py query "What are the benefits of RAG?" doc_id=<doc_id>

# Query with a specific model
./test_api.py query "What is RAG?" model=llama2

# List available models
./test_api.py models

# Show system statistics
./test_api.py stats

# Clear all data
./test_api.py clear
```

This script is useful for testing the API and for understanding how to integrate the Metis RAG system with other applications.

## API Endpoints

- `/upload` - Upload documents
- `/query` - Query documents
- `/documents` - List documents
- `/stats` - Get system statistics
- `/clear` - Clear all data
- `/system/models` - List available models
- `/system/models/{model_name}` - Switch to a specific model
- `/auth/token` - Get authentication token

## Troubleshooting

### Common Issues

1. **Ollama Connection Issues**:
   - Ensure Ollama is running with `ollama serve`
   - Check that the OLLAMA_BASE_URL in .env is correct (http://localhost:11434 for local deployment)
   - Verify that required models are pulled with `ollama list`

2. **Document Processing Issues**:
   - Check logs for errors during document processing
   - Ensure the document format is supported (.txt, .pdf, .docx)
   - Verify that the uploads directory exists and is writable

3. **Authentication Issues**:
   - If authentication is enabled, ensure the correct credentials are used
   - Check that AUTH_ENABLED is set to the desired value in .env
   - For API access, ensure the correct token is included in requests

4. **Vector Store Issues**:
   - If you encounter errors with the vector store, try clearing it with the /clear endpoint
   - Check that the chroma_db directory exists and is writable
   - Ensure the `einops` package is installed for the SentenceTransformer embedding model
   - If you see trust_remote_code errors, make sure the SentenceTransformerEmbeddings is initialized with `model_kwargs={"trust_remote_code": True}`

### Logs

Check the logs for detailed error information:
```bash
cat logs/app.log | tail -n 50
```

## Project Structure

```
metis-rag/
├── src/
│   ├── api/
│   │   ├── models/
│   │   │   ├── auth.py
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── system.py
│   │   │   └── web.py
│   │   ├── dependencies.py
│   │   └── error_handlers.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging_config.py
│   │   ├── ollama_client.py
│   │   └── text_generation.py
│   ├── rag/
│   │   ├── document_processor.py
│   │   ├── query_engine.py
│   │   └── vector_store.py
│   └── main.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       ├── base.html
│       ├── chat.html
│       ├── documents.html
│       ├── error.html
│       ├── index.html
│       ├── login.html
│       └── stats.html
├── Test_Docs/
│   ├── rag_overview.txt
│   └── authentication_security.txt
├── uploads/
├── chroma_db/
├── chat_histories/
├── logs/
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
├── start_docker.sh
└── test_api.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG components
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Ollama](https://ollama.ai/) for local language models
<<<<<<< HEAD
- [Chroma](https://www.trychroma.com/) for vector storage
=======
- [Chroma](https://www.trychroma.com/) for vector storage
>>>>>>> 6f10e44 (Initial commit of Metis RAG project)
>>>>>>> adbadd8 (Resolve merge conflict in README.md)
