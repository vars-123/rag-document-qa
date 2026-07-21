# PROJECT.md

# RAG-Powered PDF Document Question Answering System

## Project Overview

This project aims to build a production-quality Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions in natural language.

Instead of relying only on the Large Language Model's pretrained knowledge, the application retrieves relevant information from uploaded documents and uses that context to generate accurate, context-aware responses.

The project is intended to serve as a portfolio-quality application while teaching professional software engineering practices.

---

# Project Goals

The application should demonstrate:

- Modern Full Stack Development
- AI Application Development
- Retrieval-Augmented Generation (RAG)
- REST API Design
- React Frontend Development
- FastAPI Backend Development
- Vector Search
- Semantic Search
- OpenAI Integration
- Cloud Deployment
- Professional Git Workflow

The emphasis is on understanding every concept rather than simply producing working code.

---

# Target Users

Users who need to:

- Upload PDFs
- Search documents using natural language
- Obtain accurate answers based on uploaded documents
- Maintain conversation history
- Receive fast streaming responses

---

# Functional Requirements

The application should support:

### PDF Management

- Upload PDF documents
- Validate uploaded files
- Store uploaded documents
- Display uploaded documents
- Delete uploaded documents (future enhancement)

---

### Text Processing

- Extract text from PDFs
- Clean extracted text
- Split text into chunks
- Configure chunk size
- Configure chunk overlap

---

### Embeddings

Generate embeddings for every chunk using OpenAI embeddings.

Store embeddings inside ChromaDB.

---

### Vector Database

Use ChromaDB for:

- storing embeddings
- semantic similarity search
- document retrieval

---

### Question Answering

Users should be able to:

- ask questions
- retrieve relevant document chunks
- generate AI responses
- receive citations if implemented later

---

### Chat

Support:

- multiple questions
- conversation history
- streaming AI responses

---

### Frontend

React application should provide:

- clean UI
- PDF upload page
- chat interface
- loading states
- streaming messages
- error handling
- responsive design

---

### Backend

FastAPI should expose APIs for:

- upload PDF
- process document
- ask question
- retrieve chat history
- health check

---

# Non-Functional Requirements

The application should be:

- modular
- scalable
- maintainable
- readable
- reusable
- production-ready
- interview-ready

---

# Tech Stack

## Frontend

- React
- Vite
- TypeScript (preferred)
- Axios
- React Router
- CSS / Tailwind CSS (to be decided)

---

## Backend

- Python
- FastAPI
- LangChain
- ChromaDB
- OpenAI API
- Pydantic

---

## Version Control

- Git
- GitHub

---

## Deployment

Frontend

- Vercel

Backend

- Railway

Alternative

- Render

---

# Repository Structure

```
rag-document-qa/

    frontend/

    backend/

    README.md

    PROJECT.md

    AGENTS.md
```

---

# High-Level Architecture

```
User

↓

React Frontend

↓

FastAPI Backend

↓

LangChain

↓

ChromaDB

↓

OpenAI API

↓

Response

↓

React UI
```

---

# Development Milestones

## Phase 1

Project Initialization

Goals

- Repository setup
- Folder structure
- Frontend initialization
- Backend initialization
- Git setup

Deliverable

Working project structure

---

## Phase 2

Application Architecture

Goals

- Define architecture
- Folder organization
- API planning
- Data flow
- Environment configuration

Deliverable

Architecture documentation

---

## Phase 3

PDF Upload

Goals

- Upload PDFs
- Validate files
- Store files
- Test uploads

Deliverable

Working upload feature

---

## Phase 4

PDF Processing

Goals

- Extract text
- Clean text
- Chunk documents

Deliverable

Processed document

---

## Phase 5

Embedding Generation

Goals

- Generate embeddings
- Store vectors
- Verify vector storage

Deliverable

Searchable document

---

## Phase 6

Question Answering

Goals

- User query
- Vector search
- Context retrieval
- GPT response

Deliverable

Working RAG pipeline

---

## Phase 7

Streaming Responses

Goals

- Streaming API
- Frontend streaming UI

Deliverable

ChatGPT-style responses

---

## Phase 8

Chat History

Goals

- Conversation storage
- Session handling

Deliverable

Persistent conversations

---

## Phase 9

UI Improvements

Goals

- Better UX
- Loading indicators
- Error messages
- Responsive layout

Deliverable

Polished interface

---

## Phase 10

Deployment

Goals

- Deploy frontend
- Deploy backend
- Configure environment variables
- Production testing

Deliverable

Live application

---

# Engineering Standards

Every milestone must include:

- Architecture discussion
- Design decisions
- Folder updates
- Code implementation
- Testing
- Debugging
- Documentation
- Git commit
- Git push
- Review

---

# Git Workflow

Every completed milestone should end with:

```
git status

git add .

git commit

git push
```

Use Conventional Commits.

Examples

```
feat:

fix:

docs:

refactor:

test:

style:

chore:
```

---

# Documentation Requirements

Continuously maintain:

README

Architecture Notes

API Documentation

Setup Guide

Deployment Guide

Environment Variables

Future Improvements

Known Limitations

---

# Testing Requirements

Every completed feature must include:

Manual Testing

Expected Output

Edge Cases

Failure Cases

Validation

---

# Future Enhancements

Possible improvements after MVP:

- Multiple PDF support
- Authentication
- User accounts
- Document management
- Multiple LLM providers
- Source citations
- Reranking
- Hybrid Search
- OCR for scanned PDFs
- Admin Dashboard
- Analytics
- Rate limiting
- Conversation export

---

# Success Criteria

The project is considered complete when:

- Users can upload PDFs.
- Documents are processed successfully.
- Embeddings are generated.
- ChromaDB stores vectors.
- Questions retrieve relevant chunks.
- OpenAI generates accurate responses.
- Responses stream to the UI.
- Frontend is deployed on Vercel.
- Backend is deployed on Railway.
- The project is fully documented.
- Every major engineering decision is understood and can be explained during interviews.

---

# Primary Objective

This project is not only about building an AI application.

The primary objective is to become capable of independently designing, developing, debugging, deploying, and explaining a production-quality RAG system using modern software engineering practices.