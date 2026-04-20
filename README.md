# Grocery Tracker

Full-stack grocery receipt tracker with:

- FastAPI backend
- React + Vite frontend
- PostgreSQL database
- Chroma vector database
- Gemini-powered receipt and chat features

## Project Structure

- `backend_python_fastAPI/` - FastAPI API, database schema, Gemini integration
- `frontend/` - React dashboard
- `docker-compose.yml` - Full local stack with Docker

## Environment Files

Two `.env` files matter in this repo:

1. Root `.env`
   Used by `docker compose` and shared local defaults.
2. `backend_python_fastAPI/.env`
   Used when running the FastAPI app manually from the backend folder.

### Required Gemini variables

These model names now live in the `.env` files instead of being declared in Python:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_ROUTING_MODEL=gemini-2.5-flash
GEMINI_PLANNING_MODEL=gemini-2.5-flash-lite
GEMINI_SQL_MODEL=gemini-2.5-flash
GEMINI_RESPONSE_MODEL=gemini-2.5-flash-lite
GEMINI_RECEIPT_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIMENSIONALITY=768
```

## Run Manually

### 1. Prepare the environment

Copy `.env.example` values into:

- `.env`
- `backend_python_fastAPI/.env`

Set at least:

- `GEMINI_API_KEY`
- `DATABASE_URL`
- `CHROMA_HOST`
- `CHROMA_PORT`
- `VITE_API_URL`

### 2. Start PostgreSQL

Run Postgres locally with Docker:

```bash
docker run --name grocery-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password123 -e POSTGRES_DB=grocery -p 5432:5432 -d postgres:15-alpine
```

### 3. Initialize the database schema

Run the SQL bootstrap script once:

```bash
docker exec -i grocery-db psql -U postgres -d grocery < backend_python_fastAPI/init.sql
```

### 4. Start Chroma

Run Chroma locally:

```bash
docker run --name grocery-chroma -p 8000:8000 -d chromadb/chroma:latest
```

### 5. Start the backend

Open a terminal in `backend_python_fastAPI/` and run:

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open another terminal in `frontend/` and run:

```bash
npm install
npm run dev
```

Frontend URL:

- App: `http://localhost:5173`

## Run With Docker Compose

### 1. Prepare the root `.env`

Make sure the root `.env` contains:

- `GEMINI_API_KEY`
- `GEMINI_ROUTING_MODEL`
- `GEMINI_PLANNING_MODEL`
- `GEMINI_SQL_MODEL`
- `GEMINI_RESPONSE_MODEL`
- `GEMINI_RECEIPT_MODEL`
- `GEMINI_EMBEDDING_MODEL`
- `GEMINI_EMBEDDING_DIMENSIONALITY`
- `VITE_API_URL=http://localhost:8080`

### 2. Build and start all services

From the repo root:

```bash
docker compose up --build
```

This starts:

- `db` on `localhost:5432`
- `chroma` on `localhost:8000`
- `backend` on `localhost:8080`
- `frontend` on `localhost:80`

### 3. Open the app

- Frontend: `http://localhost`
- Backend API: `http://localhost:8080`
- Backend docs: `http://localhost:8080/docs`

### 4. Stop the stack

```bash
docker compose down
```

To also remove named volumes:

```bash
docker compose down -v
```

## Helpful Commands

Restart only the backend:

```bash
docker compose up --build backend
```

View logs:

```bash
docker compose logs -f
```

Check running containers:

```bash
docker ps
```
