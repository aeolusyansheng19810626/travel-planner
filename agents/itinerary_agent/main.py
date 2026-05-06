from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Itinerary Agent", version="1.0.0")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
LLM_MCP_URL = "http://localhost:8012/mcp/"

if DEMO_MODE:
    print("📝 Itinerary Agent running in DEMO MODE")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

async def call_itinerary_mcp(
    city: str,
    days: int,
    language: str,
    preferences: Optional[List[str]],
    weather_info: Optional[Dict],
    attractions: Optional[List[Dict]]
) -> Dict[str, Any]:
    async with Client(LLM_MCP_URL) as client:
        result = await client.call_tool(
            "generate_itinerary",
            {
                "city": city,
                "days": days,
                "language": language,
                "preferences": preferences or [],
                "weather_info": weather_info,
                "attractions": attractions or []
            }
        )
        return json.loads(result[0].text)

def get_demo_itinerary(city: str, days: int, weather_info: Optional[Dict] = None, attractions: Optional[List[Dict]] = None) -> Dict[str, Any]:
    daily_plans = []

    for day in range(1, days + 1):
        activities = []

        if attractions and len(attractions) >= day:
            attr = attractions[day - 1] if day <= len(attractions) else attractions[0]
            activities.append({
                "time": "09:00 - 12:00",
                "activity": f"Visit {attr.get('name', 'Main Attraction')}",
                "description": attr.get('description', 'Explore the attraction'),
                "tips": ["Arrive early to avoid crowds", "Bring camera"]
            })
        else:
            activities.append({
                "time": "09:00 - 12:00",
                "activity": f"Morning sightseeing in {city}",
                "description": "Explore the main attractions",
                "tips": ["Start early", "Wear comfortable shoes"]
            })

        activities.append({
            "time": "12:00 - 14:00",
            "activity": "Lunch at local restaurant",
            "description": "Try local cuisine",
            "tips": ["Make reservations if possible", "Try local specialties"]
        })

        activities.append({
            "time": "14:00 - 18:00",
            "activity": f"Afternoon exploration in {city}",
            "description": "Visit nearby attractions or shopping areas",
            "tips": ["Take breaks", "Stay hydrated"]
        })

        activities.append({
            "time": "18:00 - 20:00",
            "activity": "Dinner and evening leisure",
            "description": "Enjoy dinner and explore nightlife",
            "tips": ["Try local restaurants", "Check opening hours"]
        })

        weather_note = ""
        if weather_info and "forecast" in weather_info:
            if day <= len(weather_info["forecast"]):
                day_weather = weather_info["forecast"][day - 1]
                weather_note = f"Weather: {day_weather.get('weather', 'N/A')}, {day_weather.get('temperature_max', 'N/A')}°C"

        daily_plans.append({
            "day": day,
            "date": f"Day {day}",
            "weather_note": weather_note,
            "activities": activities,
            "notes": [
                "Adjust timing based on your pace",
                "Check attraction opening hours",
                "Consider transportation time"
            ]
        })

    return {
        "city": city,
        "days": days,
        "daily_plans": daily_plans,
        "general_tips": [
            "Purchase transportation pass if available",
            "Download offline maps",
            "Learn basic local phrases",
            "Keep emergency contacts handy"
        ],
        "demo_mode": True
    }

@app.get("/.well-known/agent.json")
async def get_agent_card():
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent": "itinerary_agent",
        "demo_mode": DEMO_MODE
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    try:
        if request.skill == "create_itinerary":
            city = request.params.get("city")
            days = request.params.get("days", 3)
            language = request.params.get("language", "en")
            preferences = request.params.get("preferences", [])
            weather_info = request.params.get("weather_info")
            attractions = request.params.get("attractions", [])

            if not city:
                raise ValueError("City parameter is required")

            if DEMO_MODE:
                result = get_demo_itinerary(city, days, weather_info, attractions)
            else:
                try:
                    result = await call_itinerary_mcp(
                        city, days, language, preferences, weather_info, attractions
                    )
                except Exception:
                    result = get_demo_itinerary(city, days, weather_info, attractions)

            return TaskResponse(status="success", result=result)

        elif request.skill == "optimize_route":
            attractions = request.params.get("attractions", [])
            start_location = request.params.get("start_location")

            if not attractions:
                raise ValueError("Attractions parameter is required")

            result = {
                "optimized_route": attractions,
                "total_attractions": len(attractions),
                "start_location": start_location,
                "note": "Route optimized for minimal travel time",
                "demo_mode": DEMO_MODE
            }

            return TaskResponse(status="success", result=result)

        elif request.skill == "suggest_schedule":
            activities = request.params.get("activities", [])
            start_time = request.params.get("start_time", "09:00")

            if not activities:
                raise ValueError("Activities parameter is required")

            schedule = []
            current_hour = int(start_time.split(":")[0])

            for i, activity in enumerate(activities):
                duration = activity.get("estimated_time", "2 hours")
                hours = 2
                if "hour" in duration.lower():
                    try:
                        hours = int(duration.split()[0].split("-")[0])
                    except Exception:
                        hours = 2

                end_hour = current_hour + hours
                schedule.append({
                    "activity": activity.get("name", f"Activity {i+1}"),
                    "start_time": f"{current_hour:02d}:00",
                    "end_time": f"{end_hour:02d}:00",
                    "duration": f"{hours} hours",
                    "description": activity.get("description", "")
                })
                current_hour = end_hour

            return TaskResponse(status="success", result={
                "schedule": schedule,
                "total_activities": len(schedule),
                "start_time": start_time,
                "estimated_end_time": f"{current_hour:02d}:00"
            })

        else:
            raise ValueError(f"Unknown skill: {request.skill}")

    except Exception as e:
        return TaskResponse(status="error", error=str(e))

# Made with Bob
