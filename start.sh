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

# Start orchestrator
start_service "Orchestrator" "cd orchestrator && uvicorn main:app --host 0.0.0.0 --port 8000" 8000

# Start Streamlit UI (foreground)
echo -e "${GREEN}Starting Streamlit UI on port 7860...${NC}"
streamlit run app.py --server.port=7860 --server.address=0.0.0.0

# Made with Bob
