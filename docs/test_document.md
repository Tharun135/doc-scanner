## Sample Document for Testing

This is a test document to verify that the RAG system is working correctly after uploading documents.

### Introduction
This document contains multiple sections to create several chunks when processed by the RAG system. Each section should be processed separately to create meaningful chunks for the knowledge base.

### Technical Requirements
The RAG system should be able to:
- Process various document formats including PDF, DOCX, TXT, and Markdown
- Split documents into meaningful chunks based on content structure
- Store chunks in ChromaDB for vector search
- Enable semantic search using sentence transformers
- Provide relevance scoring for search results

### Testing Procedures
To test the RAG system:
1. Upload this document through the web interface
2. Verify that chunks are created and stored
3. Check that the dashboard shows updated statistics
4. Perform search queries to test retrieval
5. Validate that results are relevant and properly scored

### Expected Results
After uploading this document:
- Total chunks should increase from 0 to at least 3-5 chunks
- Dashboard statistics should reflect the new content
- Search functionality should be able to find relevant sections
- System health indicators should show green status

### Conclusion
This test document should demonstrate that the RAG system is functioning correctly and processing documents as expected. The chunk count should update in real-time after upload.