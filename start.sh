#!/bin/bash

# Start script for Metis RAG application

# Create required directories if they don't exist
mkdir -p uploads chroma_db chat_histories logs

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << EOL
RAG_EMBEDDING_MODEL=nomic-embed-text
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
AUTH_ENABLED=true
AUTH_SECRET_KEY=your-secret-key-here-change-in-production
AUTH_TOKEN_EXPIRE_MINUTES=60
AUTH_USERNAME=admin
AUTH_PASSWORD=securepassword

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOL
    echo ".env file created. Please edit it with your settings."
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Warning: Ollama doesn't seem to be running. Please start Ollama first."
    echo "You can download Ollama from https://ollama.ai/"
    echo "After installing, run 'ollama serve' in a separate terminal."
    echo "Then run 'ollama pull nomic-embed-text' and 'ollama pull llama2' (or your preferred model)."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the application
echo "Starting Metis RAG application..."
python -m src.main