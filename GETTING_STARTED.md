# Getting Started with Metis RAG

This guide will help you quickly set up and start using the Metis RAG system. Follow these steps to get up and running in minutes.

## Quick Start Guide

### Prerequisites

Before you begin, make sure you have:

1. **Python 3.10+** installed on your system
2. **Ollama** installed and running (download from [ollama.ai](https://ollama.ai))
3. Required models:
   - Ollama model for text generation:
     ```bash
     ollama pull llama2  # or your preferred model
     ```
   - The SentenceTransformer embedding model will be downloaded automatically when first used
   - Install the required einops package:
     ```bash
     pip install einops
     ```

### Step 1: Start the Application

The easiest way to start the application is using the provided start script:

```bash
cd /home/cqhoward/Metis_1
./start.sh
```

This script will:
- Create a virtual environment if it doesn't exist
- Install dependencies
- Create necessary directories
- Generate a default .env file if needed
- Start the application

Alternatively, if you prefer using Docker:

```bash
cd /home/cqhoward/Metis_1
./start_docker.sh
```

### Step 2: Access the Web Interface

Once the application is running, open your browser and navigate to:

```
http://localhost:8002
```

You'll be greeted with the Metis RAG home page.

### Step 3: Log In (if authentication is enabled)

If authentication is enabled (default setting), use these credentials:
- Username: `admin`
- Password: `securepassword`

You can change these in the `.env` file.

### Step 4: Upload Test Documents

1. Navigate to the **Documents** page
2. Click the **Choose Files** button
3. Select the test documents from the `Test_Docs` directory:
   - `rag_overview.txt`
   - `authentication_security.txt`
4. Click **Upload**
5. Wait for the documents to be processed (this may take a few moments)

### Step 5: Ask Questions

1. Navigate to the **Chat** page
2. Type a question in the input field, for example:
   - "What is RAG and how does it work?"
   - "What are the benefits of using RAG?"
   - "What are the best practices for password-based authentication?"
3. Click **Send**
4. View the response generated based on your documents

### Step 6: Try Advanced Features

Once you're comfortable with the basics, try these advanced features:

- **Switch Models**: Use the model selector dropdown in the Chat page to try different language models
- **Document-Specific Queries**: From the Documents page, click the "Query" button next to a specific document to ask questions about only that document
- **View Statistics**: Navigate to the Stats page to see information about your documents and system performance

## Using the API Programmatically

If you prefer to interact with the system programmatically, use the provided test script:

```bash
# Upload test documents
./test_api.py upload Test_Docs/rag_overview.txt Test_Docs/authentication_security.txt

# List all documents
./test_api.py list

# Query the system
./test_api.py query "What is RAG?"

# Show system statistics
./test_api.py stats
```

## Next Steps

- Add your own documents to the system
- Experiment with different query formulations
- Try different language models
- Explore the code to understand how the system works
- Customize the system to your needs

## Troubleshooting

If you encounter any issues:

1. Check the logs in the `logs` directory
2. Make sure Ollama is running and the required models are installed
3. Verify your `.env` configuration
4. Restart the application

For more detailed information, refer to the `README.md` file.