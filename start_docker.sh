#!/bin/bash

# Start script for Metis RAG application using Docker

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Create required directories if they don't exist
mkdir -p uploads chroma_db chat_histories logs

# Start the containers
echo "Starting Metis RAG containers..."
docker-compose up -d

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 10

# Check if models are available, pull if not
echo "Checking for required models..."
if ! docker exec -it ollama ollama list | grep -q "nomic-embed-text"; then
    echo "Pulling nomic-embed-text model..."
    docker exec -it ollama ollama pull nomic-embed-text
fi

if ! docker exec -it ollama ollama list | grep -q "llama2"; then
    echo "Pulling llama2 model..."
    docker exec -it ollama ollama pull llama2
fi

# Show logs
echo "Containers started. Showing logs (press Ctrl+C to exit logs, containers will continue running)..."
docker-compose logs -f

# Instructions for stopping
echo "To stop the containers, run: docker-compose down"