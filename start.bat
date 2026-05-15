@echo off
REM Travel Planner - Windows Local Development Startup Script

echo === Travel Planner - Starting Services ===

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Copying from .env.example
    copy .env.example .env
    echo Please edit .env file with your API keys before continuing!
    exit /b 1
)

REM Start MCP Servers first
echo Starting Weather MCP Server on port 8010...
start "Weather MCP Server" cmd /k "python mcp_servers\weather_server.py"
timeout /t 2 /nobreak >nul

echo Starting Attraction MCP Server on port 8011...
start "Attraction MCP Server" cmd /k "python mcp_servers\attraction_server.py"
timeout /t 2 /nobreak >nul

echo Starting LLM MCP Server on port 8012...
start "LLM MCP Server" cmd /k "python mcp_servers\llm_server.py"
timeout /t 3 /nobreak >nul

REM Start agents
echo Starting Weather Agent on port 8001...
start "Weather Agent" cmd /k "cd agents\weather_agent && uvicorn main:app --host 0.0.0.0 --port 8001"
timeout /t 2 /nobreak >nul

echo Starting Attraction Agent on port 8002...
start "Attraction Agent" cmd /k "cd agents\attraction_agent && uvicorn main:app --host 0.0.0.0 --port 8002"
timeout /t 2 /nobreak >nul

echo Starting Itinerary Agent on port 8003...
start "Itinerary Agent" cmd /k "cd agents\itinerary_agent && uvicorn main:app --host 0.0.0.0 --port 8003"
timeout /t 2 /nobreak >nul

REM Start orchestrator (serves API + React frontend at http://localhost:8000)
echo Starting Orchestrator on port 8000...
start "Orchestrator" cmd /k "cd orchestrator && uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Build frontend if not already built
if not exist "frontend\dist" (
    echo Building React frontend...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo.
echo === All services started. Open http://localhost:8000 ===

REM Made with Bob
