# Grocery Tracker

Full-stack grocery receipt tracker with:

- FastAPI backend
- React + Vite frontend
- PostgreSQL database
- Chroma vector database
- Gemini-powered receipt and chat features
- Rate-limited public endpoints for chat and receipt upload

## Project Structure

- `backend_python_fastAPI/` - FastAPI API, database schema, Gemini integration
- `frontend/` - React dashboard
- `docker-compose.yml` - Full local stack with Docker

## Environment Configuration Files

Use [.env.example](d:/Projects/Grocery_tracker/.env.example:1) as the source of truth for the variables that must be present. It contains the current production-oriented variable list plus notes for what each value is used for.

## Startup Scripts

The repo includes helper scripts for bringing the stack up quickly:

- `scripts/start.bat` - Docker Compose startup on Windows
- `scripts/start.sh` - Docker Compose startup on Linux/macOS
- `scripts/start-local.sh` - local non-Docker startup for Linux/macOS when PostgreSQL, Chroma, Python, and Node are installed on the machine

If you prefer the scripts, configure the matching `.env` file first and then run the one appropriate for your system.

## Scheduler

The backend starts a background receipt scheduler on application startup. Its purpose is to:

- poll for receipts uploaded with status `not_processed`
- send the stored receipt file to Gemini for extraction
- write the parsed data into PostgreSQL
- update the receipt status to `processed` or `failed`

This is why receipt upload is asynchronous: the upload endpoint stores the file and queue record first, then the scheduler completes the extraction in the background.

## AI Tools Used By Chat

The chat flow is not a plain text bot. It can use multiple backend tools to answer grounded questions:

- SQL analytics over the PostgreSQL receipt database for totals, comparisons, rankings, and trends
- semantic memory search in ChromaDB for previously stored financial insights
- Gemini planning and response models to decide which tools to use and compose the final answer

This means the assistant can answer with database-backed numbers instead of only free-form model text.

## Run Manually

### 1. Prepare the environment

Copy `.env.example` values into:

- `.env`
- `backend_python_fastAPI/.env`

Review [.env.example](d:/Projects/Grocery_tracker/.env.example:1) and fill in the values required for your machine and deployment target.

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
- Receipt scheduler: starts automatically with the FastAPI app and processes uploaded receipts in the background
- Rate limiting: chat and receipt upload endpoints are protected with `slowapi`

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

Review [.env.example](d:/Projects/Grocery_tracker/.env.example:1) and copy the required values into the root `.env`.

### 2. Build and start all services

From the repo root:

```bash
docker compose up --build
```

This starts:

- `db` on the external database port configured in `.env`
- `chroma` on the external Chroma port configured in `.env`
- `backend` on the external backend port configured in `.env`
- `frontend` on the external frontend port configured in `.env`

### 3. Open the app

- Frontend: open the configured public host and frontend port
- Backend API: open the configured public host and backend port
- Backend docs: append `/docs` to the backend API URL

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

## Security Notes

- Keep real secrets only in local or hosting environment variables, never in frontend code.
- `.env` and `backend_python_fastAPI/.env` are ignored by git in this repo.
- Public-facing endpoints for `chat` and `receipts/upload` are rate limited to reduce abuse and accidental AI spend.
