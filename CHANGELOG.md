# Changelog

All notable changes to this project will be documented here.

This project follows semantic versioning.

---

## [0.4.0] - Automatic Ingestion Pipeline

### Changed

- Upload now runs the full ingestion pipeline (extract, chunk, embed) automatically in a background task
- Frontend polls document status and auto-opens chat when a document is ready
- Document statuses surfaced as user-friendly labels (Queued, Processing, Embedding, Ready, Failed)

### Added

- `POST /api/documents/{id}/retry` for failed documents
- `error` field on document responses

### Removed

- Manual `POST /api/documents/{id}/process` and `POST /api/documents/{id}/embed` endpoints and their UI buttons

## [0.3.0] - Conversation Management

### Added

- Conversation sidebar per document (list, switch, resume on refresh)
- `GET /api/chat/conversations` endpoint with title, timestamps, message count
- Auto-titling of conversations from the first question
- "New chat" action replacing the old destructive "Clear"

## [0.2.0] - Per-Client Isolation and Streaming Fix

### Fixed

- Empty chat stream ("...") caused by Gemini content-block responses
- Cross-user data leakage: documents, sessions, and history are now isolated per client via `X-Client-Id`

### Added

- `owner_id` on documents and chat sessions (with SQLite migrations)
- Anonymous persistent client identity in the frontend

## [0.1.0] - Project Initialization

### Added

- Repository created
- AGENTS.md
- PROJECT.md
- README.md
- ARCHITECTURE.md
- CHANGELOG.md
- CONTRIBUTING.md
- frontend folder
- backend folder

### Status

Project initialized.