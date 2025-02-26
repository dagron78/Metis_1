# Metis RAG Testing Plan

This document outlines a comprehensive testing strategy for the Metis RAG system. It covers various testing approaches, test cases, and best practices to ensure the system functions correctly and reliably.

## Testing Levels

### 1. Unit Testing

Unit tests focus on testing individual components in isolation.

#### Core Components to Test:

- **OllamaClient**
  - Test connection to Ollama
  - Test model listing
  - Test error handling

- **TextGenerationService**
  - Test text generation with different models
  - Test model switching
  - Test handling of different response types

- **DocumentProcessor**
  - Test document chunking
  - Test metadata extraction
  - Test handling of different file formats

- **VectorStoreManager**
  - Test document addition
  - Test similarity search
  - Test collection statistics
  - Test document listing
  - Test SentenceTransformer embeddings with trust_remote_code

- **RAGQueryEngine**
  - Test response generation
  - Test context formatting
  - Test chat history handling

### 2. Integration Testing

Integration tests focus on testing the interaction between components.

#### Key Integration Points:

- **Document Upload and Processing**
  - Test the flow from upload to vector store
  - Verify metadata is correctly preserved

- **Query Processing**
  - Test the flow from query to response
  - Verify context retrieval and response generation

- **Authentication**
  - Test token generation and validation
  - Test protected endpoints

- **Model Switching**
  - Test switching between different models
  - Verify the system uses the correct model

### 3. End-to-End Testing

End-to-end tests verify the entire system works as expected from a user's perspective.

#### Key Workflows:

- **Document Management**
  - Upload documents
  - List documents
  - Clear documents

- **Question Answering**
  - Ask questions about uploaded documents
  - Verify answers are accurate and relevant
  - Test with different models

- **Web Interface**
  - Test navigation
  - Test document upload
  - Test chat interface
  - Test statistics page

### 4. Performance Testing

Performance tests evaluate the system's performance under various conditions.

#### Areas to Test:

- **Document Processing**
  - Test with large documents
  - Test with many documents
  - Measure processing time

- **Query Response Time**
  - Measure time to retrieve context
  - Measure time to generate response
  - Test with different models

- **Concurrent Users**
  - Test with multiple simultaneous users
  - Measure system responsiveness

## Specific Test Cases

### Document Processing Tests

1. **Basic Text Document**
   - Upload a simple text document
   - Verify it's processed correctly
   - Verify chunks are created

2. **PDF Document**
   - Upload a PDF document
   - Verify text extraction
   - Verify metadata extraction

3. **DOCX Document**
   - Upload a DOCX document
   - Verify text extraction
   - Verify metadata extraction

4. **Large Document**
   - Upload a large document (>1MB)
   - Verify it's processed correctly
   - Measure processing time

5. **Multiple Documents**
   - Upload multiple documents simultaneously
   - Verify all are processed correctly

### Query Tests

1. **Basic Query**
   - Upload a document with known content
   - Ask a simple question about the content
   - Verify the answer is correct

2. **Complex Query**
   - Upload documents with related content
   - Ask a question that requires synthesizing information
   - Verify the answer correctly combines information

3. **Out-of-Scope Query**
   - Ask a question not covered by the documents
   - Verify the system acknowledges it doesn't know

4. **Document-Specific Query**
   - Upload multiple documents
   - Ask a question specific to one document
   - Verify the answer only uses that document

5. **Model-Specific Query**
   - Ask the same question with different models
   - Compare response quality and time

### Authentication Tests

1. **Valid Credentials**
   - Log in with valid credentials
   - Verify access to protected endpoints

2. **Invalid Credentials**
   - Attempt to log in with invalid credentials
   - Verify access is denied

3. **Token Expiration**
   - Log in and get a token
   - Wait for token to expire
   - Verify access is denied

4. **Protected Endpoints**
   - Attempt to access protected endpoints without authentication
   - Verify access is denied

### Error Handling Tests

1. **Invalid Document Format**
   - Upload a document with unsupported format
   - Verify appropriate error message

2. **Ollama Connection Failure**
   - Simulate Ollama being unavailable
   - Verify appropriate error handling

3. **Invalid Model**
   - Attempt to switch to a non-existent model
   - Verify appropriate error message

4. **Malformed Query**
   - Send a malformed query request
   - Verify appropriate error handling

## Testing Tools and Approaches

### Automated Testing

- **pytest**: For unit and integration tests
- **pytest-asyncio**: For testing async functions
- **pytest-httpx**: For mocking HTTP requests
- **requests**: For API testing

### Manual Testing

- **Web Interface Testing**: Test the web interface manually
- **Exploratory Testing**: Explore the system to find edge cases
- **Usability Testing**: Evaluate the user experience

### Performance Testing

- **locust**: For load testing
- **time**: For measuring execution time
- **memory_profiler**: For measuring memory usage

## Test Environment Setup

1. **Local Development Environment**
   - Python 3.10+
   - Ollama with required models
   - SentenceTransformer with nomic-ai/nomic-embed-text-v1 model
   - Virtual environment with dependencies including einops

2. **CI/CD Environment**
   - GitHub Actions or similar
   - Docker containers for isolation
   - Automated test runs on pull requests

3. **Production-Like Environment**
   - Similar to production setup
   - Realistic data volumes
   - Performance testing

## Test Data

1. **Sample Documents**
   - Small text documents
   - Large text documents
   - PDF documents
   - DOCX documents

2. **Sample Queries**
   - Simple factual queries
   - Complex analytical queries
   - Out-of-scope queries

3. **Test Users**
   - Admin user
   - Regular user
   - Unauthenticated user

## Testing Schedule

1. **Unit Tests**: Run on every code change
2. **Integration Tests**: Run on every pull request
3. **End-to-End Tests**: Run before releases
4. **Performance Tests**: Run weekly or before major releases

## Reporting and Metrics

1. **Test Coverage**: Aim for >80% code coverage
2. **Performance Metrics**:
   - Document processing time
   - Query response time
   - Memory usage
3. **Error Rates**: Track and minimize error rates

## Continuous Improvement

1. **Bug Tracking**: Document and track all bugs
2. **Test Refinement**: Continuously improve tests based on bugs found
3. **Automation**: Increase test automation over time

## Conclusion

This testing plan provides a comprehensive approach to testing the Metis RAG system. By following this plan, we can ensure the system is reliable, performant, and provides accurate responses to user queries.

Regular review and updates to this plan are recommended as the system evolves and new features are added.