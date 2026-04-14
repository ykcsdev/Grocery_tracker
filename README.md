# Grocery Tracker

Full stack application for tracking grocery spending and insights.

## Database Setup

**1. Create container**
Run PostgreSQL database container on port 5432.
```bash
docker run --name grocery-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=grocery -p 5432:5432 -d postgres:15
```

**2. Initialize schema**
Execute the SQL script to create tables sequentially.
```bash
docker exec -i grocery-db psql -U postgres -d grocery < backend_python_fastAPI/init.sql
```

## Running the Application

**Backend (FastAPI)**
Install Python dependencies, then start the server.
```bash
cd backend_python_fastAPI
python -m uvicorn app.main:app --reload
```
API Documentation: http://127.0.0.1:8000/docs


**Frontend (React)**
Navigate to frontend, install packages, and start dev server.
```bash
cd frontend
npm install
npm run dev
```
Dashboard: http://localhost:5173
