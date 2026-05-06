from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import requests
from pathlib import Path
import asyncio
from graph import create_travel_planner_graph, TravelPlanState

app = FastAPI(title="Travel Planner Orchestrator", version="1.0.0")

# Agent registry
agent_registry: Dict[str, Dict[str, Any]] = {}

# Create LangGraph workflow
travel_planner_graph = create_travel_planner_graph()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    messages: Optional[List[str]] = None

def discover_agents():
    """Discover all agents via A2A protocol"""
    import time
    
    agent_ports = {
        "weather_agent": 8001,
        "attraction_agent": 8002,
        "itinerary_agent": 8003
    }
    
    discovered = {}
    max_retries = 3
    retry_delay = 2  # seconds
    
    for agent_name, port in agent_ports.items():
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"http://localhost:{port}/.well-known/agent.json",
                    timeout=5
                )
                
                if response.status_code == 200:
                    agent_card = response.json()
                    discovered[agent_name] = agent_card
                    print(f"✓ Discovered {agent_name} at port {port}")
                    break
                else:
                    print(f"✗ Attempt {attempt + 1}/{max_retries}: {agent_name} returned HTTP {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                print(f"✗ Attempt {attempt + 1}/{max_retries}: Failed to discover {agent_name}: {e}")
            
            # Wait before retry (except last attempt)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        # All retries failed
        if agent_name not in discovered:
            print(f"✗ Failed to discover {agent_name} after {max_retries} attempts")
    
    return discovered

@app.on_event("startup")
async def startup_event():
    """Discover agents on startup"""
    global agent_registry
    
    # Wait for other services to start
    print("Waiting for agents to start...")
    await asyncio.sleep(3)
    
    print("Starting agent discovery...")
    agent_registry = discover_agents()
    print(f"Discovery complete. Found {len(agent_registry)} agents: {list(agent_registry.keys())}")

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return A2A agent card for orchestrator"""
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "agents_discovered": len(agent_registry),
        "agents": list(agent_registry.keys())
    }

@app.get("/agents")
async def list_agents():
    """List all discovered agents"""
    return {
        "count": len(agent_registry),
        "agents": agent_registry
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a travel planning query using LangGraph workflow"""
    try:
        # Initialize state
        initial_state: TravelPlanState = {
            "query": request.query,
            "destination": "",
            "days": 3,
            "preferences": [],
            "weather_info": None,
            "attractions": None,
            "itinerary": None,
            "messages": [],
            "error": None
        }
        
        # Run the workflow
        final_state = await travel_planner_graph.ainvoke(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            return QueryResponse(
                status="error",
                error=final_state["error"],
                messages=final_state.get("messages", [])
            )
        
        # Format result
        result = {
            "language": final_state.get("language", "en"),
            "destination": final_state["destination"],
            "days": final_state["days"],
            "preferences": final_state["preferences"],
            "weather": final_state.get("weather_info"),
            "attractions": final_state.get("attractions"),
            "itinerary": final_state.get("itinerary")
        }
        
        return QueryResponse(
            status="success",
            result=result,
            messages=final_state.get("messages", [])
        )
    
    except Exception as e:
        return QueryResponse(
            status="error",
            error=str(e)
        )

@app.post("/plan")
async def create_plan(
    destination: str,
    days: int = 3,
    preferences: Optional[List[str]] = None
):
    """Create a travel plan with explicit parameters"""
    try:
        query = f"Plan a {days}-day trip to {destination}"
        if preferences:
            query += f" with interests in {', '.join(preferences)}"
        
        request = QueryRequest(query=query)
        return await process_query(request)
    
    except Exception as e:
        return QueryResponse(
            status="error",
            error=str(e)
        )

# Made with Bob
