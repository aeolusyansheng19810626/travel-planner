from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Weather Agent", version="1.0.0")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
WEATHER_MCP_URL = "http://localhost:8010/mcp/"

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

async def call_weather_mcp(city: str, days: int, language: str) -> Dict[str, Any]:
    async with Client(WEATHER_MCP_URL) as client:
        result = await client.call_tool(
            "get_weather", {"city": city, "days": days, "language": language}
        )
        return json.loads(result.content[0].text)

def get_demo_weather(city: str, days: int = 7, lang: str = "en") -> Dict[str, Any]:
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    weather_types = {
        "en": ["Partly cloudy", "Clear sky"],
        "zh": ["多云", "晴朗"],
        "ja": ["一部曇り", "快晴"]
    }
    w_types = weather_types.get(lang, weather_types["en"])

    summaries = {
        "en": f"Weather forecast for {city}: Generally pleasant with temperatures ranging from 15-25°C",
        "zh": f"{city} 天气预报: 总体宜人，温度在 15-25°C 之间",
        "ja": f"{city} の天気予報: 全体的に快適で、気温は 15〜25°C の範囲です"
    }

    return {
        "city": city,
        "country": "Demo" if lang == "en" else "演示" if lang == "zh" else "デモ",
        "forecast": [
            {
                "date": dates[i],
                "temperature_max": 25 - i,
                "temperature_min": 15 - i,
                "precipitation": 0.5 * i,
                "weather": w_types[0] if i % 2 == 0 else w_types[1],
                "wind_speed": 10 + i
            }
            for i in range(days)
        ],
        "summary": summaries.get(lang, summaries["en"]),
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
        "agent": "weather_agent",
        "demo_mode": DEMO_MODE
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    try:
        if request.skill == "get_weather_info":
            city = request.params.get("city")
            days = request.params.get("days", 7)
            lang = request.params.get("language", "en")

            if not city:
                raise ValueError("City parameter is required")

            if DEMO_MODE:
                result = get_demo_weather(city, days, lang)
            else:
                try:
                    result = await call_weather_mcp(city, days, lang)
                except Exception as e:
                    print(f"[weather_agent] MCP call failed, using demo fallback: {e}")
                    result = get_demo_weather(city, days, lang)

            return TaskResponse(status="success", result=result)

        elif request.skill == "check_weather_suitability":
            city = request.params.get("city")
            days = request.params.get("days", 7)
            lang = request.params.get("language", "en")

            if not city:
                raise ValueError("City parameter is required")

            if DEMO_MODE:
                weather_info = get_demo_weather(city, days, lang)
            else:
                try:
                    weather_info = await call_weather_mcp(city, days, lang)
                except Exception as e:
                    print(f"[weather_agent] MCP call failed, using demo fallback: {e}")
                    weather_info = get_demo_weather(city, days, lang)

            good_days = 0
            warnings = []

            for day in weather_info["forecast"]:
                is_good = True
                if day["precipitation"] > 10:
                    warnings.append(f"{day['date']}: Heavy rain expected ({day['precipitation']}mm)")
                    is_good = False
                if day["temperature_max"] > 35 or day["temperature_max"] < 0:
                    warnings.append(f"{day['date']}: Extreme temperature ({day['temperature_max']}°C)")
                    is_good = False
                if day["wind_speed"] > 40:
                    warnings.append(f"{day['date']}: Strong winds ({day['wind_speed']}km/h)")
                    is_good = False
                if is_good:
                    good_days += 1

            suitability_score = (good_days / len(weather_info["forecast"])) * 100

            result = {
                "city": weather_info["city"],
                "suitability_score": round(suitability_score, 1),
                "good_days": good_days,
                "total_days": len(weather_info["forecast"]),
                "warnings": warnings,
                "recommendation": "Good for travel" if suitability_score >= 70 else "Consider weather conditions"
            }

            return TaskResponse(status="success", result=result)

        else:
            raise ValueError(f"Unknown skill: {request.skill}")

    except Exception as e:
        return TaskResponse(status="error", error=str(e))

# Made with Bob
