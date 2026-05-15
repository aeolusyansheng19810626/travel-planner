#!/bin/bash

# Travel Planner - Local Development Startup Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Travel Planner - Starting Services ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Copying from .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file with your API keys before continuing!${NC}"
    exit 1
fi

source .env

if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    echo -e "${RED}Error: GROQ_API_KEY not set in .env file${NC}"
    exit 1
fi

if [ -z "$TAVILY_API_KEY" ] || [ "$TAVILY_API_KEY" = "your_tavily_api_key_here" ]; then
    echo -e "${RED}Error: TAVILY_API_KEY not set in .env file${NC}"
    exit 1
fi

start_service() {
    local name=$1
    local command=$2
    local port=$3
    echo -e "${GREEN}Starting $name on port $port...${NC}"
    eval "$command" &
    sleep 2
}

# Start MCP Servers first
start_service "Weather MCP Server"    "python mcp_servers/weather_server.py"    8010
start_service "Attraction MCP Server" "python mcp_servers/attraction_server.py" 8011
start_service "LLM MCP Server"        "python mcp_servers/llm_server.py"        8012

# Wait a bit longer for MCP servers to be ready
sleep 1

# Start agents
start_service "Weather Agent"    "cd agents/weather_agent    && uvicorn main:app --host 0.0.0.0 --port 8001" 8001
start_service "Attraction Agent" "cd agents/attraction_agent && uvicorn main:app --host 0.0.0.0 --port 8002" 8002
start_service "Itinerary Agent"  "cd agents/itinerary_agent  && uvicorn main:app --host 0.0.0.0 --port 8003" 8003

# Start orchestrator (also serves frontend at http://localhost:8000)
start_service "Orchestrator" "cd orchestrator && uvicorn main:app --host 0.0.0.0 --port 8000" 8000

# Build or start frontend dev server
if [ -d "frontend/dist" ]; then
    echo -e "${GREEN}Frontend already built. Serving via orchestrator at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}Building frontend...${NC}"
    cd frontend && npm install && npm run build && cd ..
    echo -e "${GREEN}Frontend built. Serving via orchestrator at http://localhost:8000${NC}"
fi

echo -e "${GREEN}=== All services started. Open http://localhost:8000 ===${NC}"
wait

# Made with Bob
