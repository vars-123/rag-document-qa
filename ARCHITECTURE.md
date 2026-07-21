# System Architecture

## Overview

This document describes the architecture of the RAG-powered PDF Question Answering application. It serves as the design blueprint for all development milestones.

---

## High-Level Flow

```
User
  │
  ▼
React Frontend  (Vite, TypeScript)
  │  HTTP / Streaming
  ▼
FastAPI Backend  (Python, Pydantic)
  │
  ├── PDF Upload → PDF Service → Chunking Service → Embedding Service → ChromaDB
  │
  └── Question → Retrieval Service → Context Builder → Chat Service → OpenAI → Streaming Response
```

---

## Folder Structure

```
rag-document-qa/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        Reusable UI components
│   │   │   ├── UploadZone.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── hooks/             Custom React hooks
│   │   │   ├── useDocuments.ts
│   │   │   └── useChat.ts
│   │   ├── services/          API client layer
│   │   │   └── api.ts
│   │   ├── types/             TypeScript interfaces
│   │   │   ├── document.ts
│   │   │   └── chat.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, middleware, router registration
│   │   ├── config.py          Pydantic Settings (env vars)
│   │   ├── routers/           API route handlers (thin, delegate to services)
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/          Business logic layer
│   │   │   ├── pdf_service.py      Extract text from PDFs
│   │   │   ├── chunking_service.py Split text into chunks
│   │   │   ├── embedding_service.py Generate & store embeddings
│   │   │   ├── vector_service.py   ChromaDB operations
│   │   │   └── chat_service.py     LLM response generation
│   │   └── models/            Pydantic request/response models
│   │       ├── document.py
│   │       └── chat.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_documents.py
│   │   └── test_chat.py
│   ├── requirements.txt
│   └── .env
│
├── ARCHITECTURE.md
├── AGENTS.md
├── PROJECT.md
├── README.md
└── CHANGELOG.md
```

---

## API Endpoints

### Health

| Method | Path          | Description     | Request | Response                     |
|--------|---------------|-----------------|---------|------------------------------|
| GET    | `/api/health` | Health check    | —       | `{ "status": "ok" }`         |

### Documents

| Method | Path                    | Description       | Request            | Response                          |
|--------|-------------------------|-------------------|--------------------|-----------------------------------|
| POST   | `/api/documents/upload` | Upload a PDF      | `multipart/form-data` (file) | `{ "id", "filename", "status" }` |
| GET    | `/api/documents`        | List documents    | —                  | `[{ "id", "filename", "status", "uploaded_at" }]` |
| DELETE | `/api/documents/{id}`   | Delete a document | —                  | `{ "status": "deleted" }`         |

### Chat

| Method | Path             | Description                          | Request                     | Response                                     |
|--------|------------------|--------------------------------------|-----------------------------|----------------------------------------------|
| POST   | `/api/chat`      | Ask a question (streaming)           | `{ "document_id", "question", "session_id"? }` | `text/event-stream` (SSE) |
| GET    | `/api/chat/history` | Get chat history for a session    | `?session_id=...`           | `[{ "role", "content", "timestamp" }]`      |

---

## Data Flow

### PDF Upload Pipeline

```
Upload PDF → Validate (.pdf, size) → Store file on disk
  → PDF Service (extract text with pdfplumber)
  → Chunking Service (split into overlapping chunks, ~500 tokens)
  → Embedding Service (OpenAI text-embedding-3-small)
  → Vector Service (store in ChromaDB collection)
  → Return document ID + status
```

### Question Answering Pipeline

```
User sends question + document_id
  → Vector Service (semantic search in ChromaDB, top-k chunks)
  → Context Builder (concatenate retrieved chunks)
  → Chat Service (build prompt with context + question)
  → OpenAI streaming response (ChatCompletion with stream=True)
  → SSE stream to frontend
  → Frontend renders tokens as they arrive
```

---

## Service Layer Responsibilities

| Service            | Responsibility                                          |
|--------------------|---------------------------------------------------------|
| `pdf_service`      | Extract raw text from PDF using pdfplumber              |
| `chunking_service` | Split text using LangChain `RecursiveCharacterTextSplitter` |
| `embedding_service`| Generate embeddings via `OpenAIEmbeddings` (LangChain)   |
| `vector_service`   | CRUD on ChromaDB collections; similarity search          |
| `chat_service`     | Build prompt, stream response from `ChatOpenAI`          |

Routers **must not** contain business logic — they validate input, call a service, and return the response.

---

## Environment Variables

| Variable           | Required | Default            | Description                      |
|--------------------|----------|--------------------|----------------------------------|
| `OPENAI_API_KEY`   | Yes      | —                  | OpenAI API key                   |
| `CHROMA_DB_PATH`   | No       | `./chroma_db`      | Persistence path for ChromaDB    |
| `DATABASE_URL`     | No       | `sqlite:///./chat.db` | Database for chat history     |
| `FRONTEND_URL`     | No       | `http://localhost:5173` | Allowed CORS origin          |

---

## Key Design Decisions

1. **Service layer abstraction** — routers stay thin; all logic lives in services. Enables unit testing without HTTP.
2. **Streaming via SSE** — Server-Sent Events for chat responses. Simpler than WebSockets for unidirectional streaming.
3. **ChromaDB embedded** — runs in-process. Simple to set up; no external server needed. Can migrate to self-hosted later.
4. **LangChain for orchestration** — provides standard interfaces for text splitting, embeddings, and LLM calls. Reduces boilerplate.
5. **Pydantic v2** — used for both config (`BaseSettings`) and API models (`BaseModel`). Single source of truth for data shapes.
