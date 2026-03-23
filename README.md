# ChatPDF

ChatPDF is a document question answering system that allows users to upload documents and ask questions based on their content. It retrieves relevant sections from the document and generates answers using language models, ensuring responses are based only on the provided data.

---

## Features

### Document Processing
- Upload PDF and text files
- Extract and split text into chunks
- Generate embeddings and store in FAISS
- Supports local and S3-based storage

### Retrieval and Question Answering
- Semantic search using vector similarity
- Top-k relevant chunk retrieval
- Context-based answer generation

### Grounding and Safety
- Refusal when no relevant context is found
- Prevents answers outside the provided documents

### Backend
- Django-based API
- Document ownership validation
- Query logging and latency tracking

### Frontend
- Streamlit interface for uploading and querying documents
- Displays answers along with references

---

## Architecture

Document → Chunk → Embed → Index → Retrieve → Generate → Validate → Answer

---

## Tech Stack

Django  
Streamlit  
FAISS  
LangChain  
LangGraph  
AWS S3  
