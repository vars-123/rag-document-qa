# RAG-Powered PDF Document Question Answering System

## Overview

A production-quality Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and ask questions in natural language.

The system retrieves relevant information from uploaded documents using semantic search and generates accurate responses with Gemini.

---

## Project Status

🚧 In Development

Current Phase:

- Phase 10 - Deployment

Completed milestones:

- PDF upload
- Automatic ingestion pipeline (background processing and embedding)
- Embedding generation
- Question answering
- Streaming responses
- Chat history and session handling
- Per-user data isolation (client identity)
- Conversation management (sidebar, multiple conversations per document)
- Responsive UI refresh
- Deployment readiness

---

## Tech Stack

### Frontend

- React
- Vite

### Backend

- FastAPI
- Python

### AI

- LangChain
- Gemini
- Google Generative AI embeddings
- ChromaDB

### Deployment

- Vercel
- Railway

---

## Repository Structure

```text
frontend/
backend/
```

---

## Learning Goals

- Learn RAG architecture
- Learn FastAPI
- Learn React
- Learn LangChain
- Learn Vector Databases
- Learn Production Development
- Learn Deployment

---

## Running the Project

Documentation will be added as development progresses.

See [DEPLOYMENT.md](./DEPLOYMENT.md) for the production setup guide.

## Known Limitations

- Text-based PDFs process correctly.
- Scanned or image-only PDFs are not supported yet because OCR is still a future enhancement.

---

## License

MIT
