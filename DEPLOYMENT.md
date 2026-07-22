# Deployment Guide

This project is designed for a split deployment:

- Frontend on Vercel
- Backend on Railway or Render

The frontend and backend are deployed separately, so the frontend must know the backend base URL.

---

## 1. Environment Variables

### Backend

Set these in Railway or Render:

- `GOOGLE_API_KEY` - Gemini API key used by the backend for chat and embeddings
- `CHROMA_DB_PATH` - local persistence path for ChromaDB
- `DATABASE_URL` - SQLite path used for chat history
- `FRONTEND_URL` - comma-separated list of allowed frontend origins for CORS

### Frontend

Set this in Vercel:

- `VITE_API_BASE_URL` - full backend API prefix, for example `https://your-backend-domain.com/api`

---

## 2. Backend Deployment

1. Create a new Railway or Render service from the repository.
2. Set the service root to `backend/` if the platform asks for a root directory.
3. Add the backend environment variables.
4. Start the app with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Confirm the health endpoint responds at `/api/health`.

### Notes

- The backend uses CORS to allow the frontend origin list defined in `FRONTEND_URL`.
- SQLite is fine for local or demo deployments, but production persistence is limited without a mounted volume.

---

## 3. Frontend Deployment

1. Create a new Vercel project from the repository.
2. Set the project root to `frontend/`.
3. Add `VITE_API_BASE_URL` with the deployed backend URL.
4. Build with the default Vite command.
5. Verify the deployed app can upload a PDF and reach the backend health endpoint.

---

## 4. Production Checklist

- `GET /api/health` returns `{"status":"ok"}`
- CORS allows the deployed frontend domain
- PDF upload works from the deployed frontend
- Document processing and embedding still work
- Chat streaming responds from the backend domain
- Chat history is available for the selected document
- The Railway backend has `GOOGLE_API_KEY` configured and can reach the Gemini API

---

## 5. Common Issues

- A blank frontend usually means `VITE_API_BASE_URL` is missing or wrong.
- CORS errors usually mean the frontend domain is missing from `FRONTEND_URL`.
- Failed chat or embedding requests often mean the backend runtime cannot reach the Gemini API or the `GOOGLE_API_KEY` secret is missing.
- If chat history resets unexpectedly, check whether the SQLite file is stored on ephemeral disk.
