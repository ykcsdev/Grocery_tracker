@echo off
REM start.bat - Kick starts the entire Grocery Tracker Application (Windows)

echo ===============================================
echo    AI Grocery Tracker - Startup Script (Windows)  
echo ===============================================

REM Check if GEMINI_API_KEY is set, provide a warning if not
IF "%GEMINI_API_KEY%"=="" (
    echo Warning: GEMINI_API_KEY environment variable is not set in the active shell.
    echo It should be provided via the .env file for docker-compose to pick it up.
)

echo Starting instances (Postgres DB, ChromaDB, FastAPI Backend, React Frontend)...
docker-compose up --build -d

echo.
echo ===============================================
echo Application successfully started in the background!
echo Wait for the containers to fully initialize, then visit:
echo.
echo -^> Frontend App: http://localhost:80
echo -^> Backend API:  http://localhost:8080
echo ===============================================
echo.
echo To view logs, run: docker-compose logs -f
echo To stop the app, run: docker-compose down

pause
