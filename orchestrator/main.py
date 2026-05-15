from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, AsyncGenerator
import json
import requests
from pathlib import Path
import asyncio
from graph import create_travel_planner_graph, TravelPlanState

app = FastAPI(title="Travel Planner Orchestrator", version="1.0.0")

@app.middleware("http")
async def strip_api_prefix(request: Request, call_next):
    """Allow frontend to call /api/* — strip the prefix before routing."""
    if request.scope["path"].startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:]  # /api/health → /health
        request.scope["raw_path"] = request.scope["path"].encode()
    return await call_next(request)

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
    models_used: Optional[Dict[str, str]] = None

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
                    print(f"[OK] Discovered {agent_name} at port {port}")
                    break
                else:
                    print(f"[FAIL] Attempt {attempt + 1}/{max_retries}: {agent_name} returned HTTP {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"[FAIL] Attempt {attempt + 1}/{max_retries}: Failed to discover {agent_name}: {e}")

            # Wait before retry (except last attempt)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        # All retries failed
        if agent_name not in discovered:
            print(f"[FAIL] Failed to discover {agent_name} after {max_retries} attempts")
    
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
            "language": "",
            "destination": "",
            "destination_local": "",
            "country": "",
            "days": 3,
            "preferences": [],
            "weather_info": None,
            "attractions": None,
            "itinerary": None,
            "models_used": {},
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
                messages=final_state.get("messages", []),
                models_used=final_state.get("models_used", {})
            )
        
        # Format result
        result = {
            "language": final_state.get("language", "en"),
            "destination": final_state["destination"],
            "days": final_state["days"],
            "preferences": final_state["preferences"],
            "weather": final_state.get("weather_info"),
            "attractions": final_state.get("attractions"),
            "itinerary": final_state.get("itinerary"),
            "models_used": final_state.get("models_used", {})
        }
        
        return QueryResponse(
            status="success",
            result=result,
            messages=final_state.get("messages", []),
            models_used=final_state.get("models_used", {})
        )
    
    except Exception as e:
        return QueryResponse(
            status="error",
            error=str(e)
        )

def _sse_event(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def _stream_query(query: str) -> AsyncGenerator[str, None]:
    """Stream query progress as SSE events."""
    initial_state: TravelPlanState = {
        "query": query,
        "language": "",
        "destination": "",
        "days": 3,
        "preferences": [],
        "weather_info": None,
        "attractions": None,
        "itinerary": None,
        "models_used": {},
        "messages": [],
        "error": None,
    }

    accumulated: Dict[str, Any] = {**initial_state}

    try:
        async for chunk in travel_planner_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_update in chunk.items():
                # merge into accumulated state
                accumulated.update(node_update)

                if node_name == "parse_query":
                    if accumulated.get("error"):
                        yield _sse_event("fatal", {"error": accumulated["error"]})
                        return
                    yield _sse_event("parsed", {
                        "language": accumulated.get("language", ""),
                        "destination": accumulated.get("destination", ""),
                        "destination_local": accumulated.get("destination_local", ""),
                        "country": accumulated.get("country", ""),
                        "days": accumulated.get("days", 3),
                        "preferences": accumulated.get("preferences", []),
                    })

                elif node_name == "get_weather":
                    weather_info = accumulated.get("weather_info")
                    models = accumulated.get("models_used", {})
                    if weather_info:
                        yield _sse_event("weather", {
                            "weather_info": weather_info,
                            "model": models.get("weather"),
                        })
                    else:
                        yield _sse_event("weather", {"error": "weather unavailable", "stage": "weather"})

                elif node_name == "search_attractions":
                    attractions = accumulated.get("attractions")
                    models = accumulated.get("models_used", {})
                    if attractions:
                        yield _sse_event("attractions", {
                            "attractions": attractions,
                            "model": models.get("attraction_cleaner"),
                        })
                    else:
                        yield _sse_event("attractions", {"error": "attractions unavailable", "stage": "attractions"})

                elif node_name == "generate_itinerary":
                    itinerary = accumulated.get("itinerary")
                    models = accumulated.get("models_used", {})
                    if itinerary and not accumulated.get("error"):
                        yield _sse_event("itinerary", {
                            "itinerary": itinerary,
                            "model": models.get("itinerary_generator"),
                        })
                    else:
                        yield _sse_event("itinerary", {
                            "error": accumulated.get("error", "itinerary unavailable"),
                            "stage": "itinerary",
                        })

        # Emit done with final state
        final_result = {
            "language": accumulated.get("language", ""),
            "destination": accumulated.get("destination", ""),
            "destination_local": accumulated.get("destination_local", ""),
            "country": accumulated.get("country", ""),
            "days": accumulated.get("days", 3),
            "preferences": accumulated.get("preferences", []),
            "weather": accumulated.get("weather_info"),
            "attractions": accumulated.get("attractions"),
            "itinerary": accumulated.get("itinerary"),
        }
        yield _sse_event("done", {
            "full_result": final_result,
            "models_used": accumulated.get("models_used", {}),
        })

    except Exception as e:
        yield _sse_event("fatal", {"error": str(e)})


@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    """Process a travel planning query and stream progress as SSE."""
    return StreamingResponse(
        _stream_query(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
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


# Serve the built React frontend (must be last to avoid catching API routes)
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")

# Made with Bob
