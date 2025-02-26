
#!/usr/bin/env python3
"""
Test script for the Metis RAG API.
This script demonstrates how to interact with the API programmatically.
"""

import requests
import json
import sys
import os
from pathlib import Path
import time

# API URL (change if needed)
BASE_URL = os.getenv("RAG_API_URL", "http://localhost:8002")

# Authentication (if enabled)
AUTH_ENABLED = False  # Changed to False to disable authentication
AUTH_USERNAME = "admin"  # Replace with your username
AUTH_PASSWORD = "securepassword"  # Replace with your password


def get_auth_token():
    """Get authentication token if auth is enabled."""
    if not AUTH_ENABLED:
        return None

    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": AUTH_USERNAME, "password": AUTH_PASSWORD}
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting auth token: {e}")
        return None

def get_headers():
    """Get headers with authentication token if needed."""
    token = get_auth_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def test_stats():
    """Test the stats endpoint."""
    print("\n--- Testing /stats endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/stats", headers=get_headers())
        response.raise_for_status()
        stats = response.json()
        print("Stats endpoint returned successfully!")
        print(f"Vector store stats: {json.dumps(stats['vector_store_stats'], indent=2)}")
        print(f"Uploaded documents: {stats['uploaded_documents']}")
        print(f"Chat histories: {stats['chat_histories']}")
        return stats
    except requests.exceptions.RequestException as e:
        print(f"Error getting stats: {e}")
        return None

def upload_document(file_paths):
    """Upload one or more documents."""
    print(f"\n--- Uploading documents: {file_paths} ---")
    success = True

    headers = get_headers()
    if 'Content-Type' in headers:
        del headers['Content-Type']  # Remove content type for multipart/form-data

    for file_path in file_paths:
        if not Path(file_path).exists():
            print(f"Error: File {file_path} does not exist.")
            success = False
            continue

        try:
            with open(file_path, 'rb') as f:
                # Use 'files' as the parameter name, which matches the FastAPI endpoint
                files = {'files': (Path(file_path).name, f, 'application/octet-stream')}
                response = requests.post(
                    f"{BASE_URL}/upload",
                    files=files,
                    headers=headers  # Pass headers here
                )
                response.raise_for_status()
                result = response.json()
                print(f"Upload successful for {file_path}: {result['message']}")
                print(f"  Document IDs: {result['document_ids']}")
        except requests.exceptions.RequestException as e:
            print(f"Error uploading {file_path}: {e}")
            success = False

    return success

def list_documents():
    """List all documents."""
    print("\n--- Listing documents ---")
    try:
        response = requests.get(f"{BASE_URL}/documents", headers=get_headers())
        response.raise_for_status()
        result = response.json()
        print(f"Total documents: {result['total_documents']}")
        print(f"Total chunks: {result['total_chunks']}")

        if result['documents']:
            print("\nDocument list:")
            for doc in result['documents']:
                print(f"  - ID: {doc['doc_id']}, File: {doc['file_name']} ({doc['file_type']}), Chunks: {doc['chunk_count']}, Source: {doc['source']}")
        else:
            print("No documents found in the system.")
        return result['documents']
    except requests.exceptions.RequestException as e:
        print(f"Error listing documents: {e}")
        return []

def test_query(query_text, model_name=None, doc_id=None, chat_history_id = None):
    """Test the query endpoint."""
    print(f"\n--- Testing query: '{query_text}' ---")
    payload = {"query": query_text}
    if model_name:
        payload["model_name"] = model_name
    if doc_id:
        payload["doc_id"] = doc_id
    if chat_history_id:
        payload["chat_history_id"] = chat_history_id

    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers=get_headers()  # Pass headers here
        )
        response.raise_for_status()
        result = response.json()
        print("Query successful!")
        print(f"\nResponse: {result['response']}")
        print(f"Chat history ID: {result['chat_history_id']}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error querying: {e}")
        return None

def list_models():
    """List available models."""
    print("\n--- Listing models ---")
    try:
        response = requests.get(f"{BASE_URL}/system/models", headers=get_headers())
        response.raise_for_status()
        result = response.json()
        print("Available models:")
        for model in result['models']:
            print(f"  - {model['name']}")
        return result['models']
    except requests.exceptions.RequestException as e:
        print(f"Error listing models: {e}")
        return []

def main():
    """Main function."""
    print("=== Metis RAG API Test ===")

    # Check if the API is available
    try:
        requests.get(f"{BASE_URL}/system/health", headers=get_headers())
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to {BASE_URL}. Make sure the server is running.")
        sys.exit(1)

    # Process command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "upload" and len(sys.argv) > 2:
            file_paths = sys.argv[2:]
            if upload_document(file_paths):
                print("\nWaiting for background processing to complete...")
                time.sleep(5)
                test_stats()
                list_documents()

        elif command == "query" and len(sys.argv) > 2:
            query_text = sys.argv[2]
            model_name = None
            doc_id = None
            chat_history_id = None

            # Very basic argument parsing.  Could use argparse for more robust handling.
            for i in range(3, len(sys.argv)):
                if sys.argv[i].startswith("model="):
                    model_name = sys.argv[i][len("model="):]
                elif sys.argv[i].startswith("doc_id="):
                    doc_id = sys.argv[i][len("doc_id="):]
                elif sys.argv[i].startswith("chat_id="):
                    chat_history_id = sys.argv[i][len("chat_id="):]

            test_query(query_text, model_name, doc_id, chat_history_id)

        elif command == "list":
            list_documents()

        elif command == "models":
            list_models()

        elif command == "stats":
            test_stats()
        
        elif command == "clear":
            try:
                response = requests.delete(f"{BASE_URL}/clear", headers=get_headers())
                response.raise_for_status()
                print(response.json()["message"])
            except requests.exceptions.RequestException as e:
                print(f"Error clearing system: {e}")

        else:
            print_usage()
    else:
        # Run all tests if no command is provided
        print("Running all tests...")
        test_stats()
        list_models()
        list_documents()
        print("\nTest script completed. Use specific commands for more detailed testing.")
        print_usage()

def print_usage():
    print("\nUsage:")
    print("  python test_api.py upload <file_path1> [<file_path2> ...]  - Upload documents")
    print("  python test_api.py query <query_text> [model=<model_name>] [doc_id=<doc_id>] [chat_id=<chat_history_id>] - Test a query")
    print("  python test_api.py list                - List documents")
    print("  python test_api.py models              - List available models")
    print("  python test_api.py stats               - Show system statistics")
    print("  python test_api.py clear               - Clear all data (vector store, uploads, chat history)")
    print(f"\nDefault API URL: {BASE_URL} (set RAG_API_URL environment variable to override)")

if __name__ == "__main__":
    main()