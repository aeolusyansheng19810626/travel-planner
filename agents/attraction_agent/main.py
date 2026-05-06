from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Attraction Agent", version="1.0.0")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
ATTRACTION_MCP_URL = "http://localhost:8011/mcp/"

if DEMO_MODE:
    print("🔍 Attraction Agent running in DEMO MODE")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

async def call_attraction_mcp(
    city: str,
    preferences: Optional[List[str]],
    max_results: int,
    language: str
) -> Dict[str, Any]:
    async with Client(ATTRACTION_MCP_URL) as client:
        result = await client.call_tool(
            "search_attractions",
            {
                "city": city,
                "preferences": preferences or [],
                "max_results": max_results,
                "language": language
            }
        )
        return json.loads(result[0].text)

def get_demo_attractions(city: str, preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    attractions_db = {
        "Tokyo": [
            {
                "name": "Senso-ji Temple",
                "description": "Tokyo's oldest temple, a symbol of Asakusa with beautiful architecture",
                "category": "historical",
                "rating": 4.5,
                "estimated_time": "1-2 hours",
                "best_time": "Morning"
            },
            {
                "name": "Tokyo Skytree",
                "description": "Tallest structure in Japan with panoramic city views",
                "category": "landmark",
                "rating": 4.6,
                "estimated_time": "2-3 hours",
                "best_time": "Evening"
            },
            {
                "name": "Tsukiji Outer Market",
                "description": "Famous food market with fresh seafood and street food",
                "category": "food",
                "rating": 4.4,
                "estimated_time": "2-3 hours",
                "best_time": "Morning"
            },
            {
                "name": "Meiji Shrine",
                "description": "Peaceful Shinto shrine surrounded by forest in the heart of Tokyo",
                "category": "historical",
                "rating": 4.5,
                "estimated_time": "1-2 hours",
                "best_time": "Morning"
            },
            {
                "name": "Shibuya Crossing",
                "description": "World's busiest pedestrian crossing, iconic Tokyo experience",
                "category": "landmark",
                "rating": 4.3,
                "estimated_time": "30 minutes",
                "best_time": "Evening"
            }
        ],
        "Osaka": [
            {
                "name": "Osaka Castle",
                "description": "Historic castle with museum and beautiful gardens",
                "category": "historical",
                "rating": 4.4,
                "estimated_time": "2-3 hours",
                "best_time": "Morning"
            },
            {
                "name": "Dotonbori",
                "description": "Famous entertainment district with neon lights and street food",
                "category": "food",
                "rating": 4.5,
                "estimated_time": "2-3 hours",
                "best_time": "Evening"
            },
            {
                "name": "Kuromon Ichiba Market",
                "description": "Osaka's kitchen with fresh seafood and local delicacies",
                "category": "food",
                "rating": 4.3,
                "estimated_time": "1-2 hours",
                "best_time": "Morning"
            },
            {
                "name": "Sumiyoshi Taisha",
                "description": "One of Japan's oldest Shinto shrines with unique architecture",
                "category": "historical",
                "rating": 4.4,
                "estimated_time": "1-2 hours",
                "best_time": "Morning"
            }
        ],
        "Kyoto": [
            {
                "name": "Fushimi Inari Shrine",
                "description": "Famous for thousands of red torii gates on mountain trails",
                "category": "historical",
                "rating": 4.7,
                "estimated_time": "2-3 hours",
                "best_time": "Early morning"
            },
            {
                "name": "Kinkaku-ji (Golden Pavilion)",
                "description": "Stunning gold-leaf covered temple by a pond",
                "category": "historical",
                "rating": 4.6,
                "estimated_time": "1 hour",
                "best_time": "Morning"
            },
            {
                "name": "Arashiyama Bamboo Grove",
                "description": "Serene bamboo forest path, iconic Kyoto experience",
                "category": "nature",
                "rating": 4.5,
                "estimated_time": "1-2 hours",
                "best_time": "Morning"
            },
            {
                "name": "Nishiki Market",
                "description": "Traditional food market known as Kyoto's kitchen",
                "category": "food",
                "rating": 4.3,
                "estimated_time": "1-2 hours",
                "best_time": "Afternoon"
            }
        ]
    }

    attractions = attractions_db.get(city, [
        {
            "name": f"{city} Main Attraction",
            "description": f"Popular tourist spot in {city}",
            "category": "landmark",
            "rating": 4.0,
            "estimated_time": "2 hours",
            "best_time": "Anytime"
        }
    ])

    if preferences:
        pref_lower = [p.lower() for p in preferences]
        filtered = [
            a for a in attractions
            if any(pref in a["category"].lower() or pref in a["description"].lower() for pref in pref_lower)
        ]
        if filtered:
            attractions = filtered

    return attractions

@app.get("/.well-known/agent.json")
async def get_agent_card():
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "attraction_agent",
        "demo_mode": DEMO_MODE
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    try:
        if request.skill == "search_attractions":
            city = request.params.get("city")
            preferences = request.params.get("preferences", [])
            max_results = request.params.get("max_results", 5)
            lang = request.params.get("language", "en")

            if not city:
                raise ValueError("City parameter is required")

            if DEMO_MODE:
                attractions = get_demo_attractions(city, preferences)
                model_used = None
            else:
                try:
                    mcp_result = await call_attraction_mcp(city, preferences, max_results, lang)
                    attractions = mcp_result.get("attractions", [])
                    model_used = mcp_result.get("model_used")
                except Exception:
                    attractions = get_demo_attractions(city, preferences)
                    model_used = None

            return TaskResponse(status="success", result={
                "city": city,
                "preferences": preferences,
                "attractions": attractions,
                "count": len(attractions),
                "model_used": model_used
            })

        elif request.skill == "get_attraction_details":
            attraction_name = request.params.get("attraction_name")
            city = request.params.get("city")

            if not attraction_name:
                raise ValueError("Attraction name parameter is required")

            result = {
                "name": attraction_name,
                "city": city,
                "description": f"Detailed information about {attraction_name}",
                "opening_hours": "9:00 AM - 6:00 PM",
                "admission_fee": "Varies",
                "tips": ["Visit early to avoid crowds", "Allow 2-3 hours for visit"],
                "demo_mode": True
            }

            return TaskResponse(status="success", result=result)

        elif request.skill == "recommend_attractions":
            city = request.params.get("city")
            preferences = request.params.get("preferences", [])
            days = request.params.get("days", 3)

            if not city:
                raise ValueError("City parameter is required")

            if DEMO_MODE:
                all_attractions = get_demo_attractions(city, preferences)
            else:
                try:
                    mcp_result = await call_attraction_mcp(city, preferences, days * 3, "en")
                    all_attractions = mcp_result.get("attractions", [])
                except Exception:
                    all_attractions = get_demo_attractions(city, preferences)

            attractions_per_day = max(2, len(all_attractions) // days)
            daily_recommendations = []

            for day in range(days):
                start_idx = day * attractions_per_day
                end_idx = start_idx + attractions_per_day
                day_attractions = all_attractions[start_idx:end_idx]
                daily_recommendations.append({
                    "day": day + 1,
                    "attractions": day_attractions,
                    "count": len(day_attractions)
                })

            return TaskResponse(status="success", result={
                "city": city,
                "days": days,
                "preferences": preferences,
                "daily_recommendations": daily_recommendations,
                "total_attractions": len(all_attractions)
            })

        else:
            raise ValueError(f"Unknown skill: {request.skill}")

    except Exception as e:
        return TaskResponse(status="error", error=str(e))

# Made with Bob
