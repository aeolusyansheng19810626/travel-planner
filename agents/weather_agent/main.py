from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import httpx
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Weather Agent", version="1.0.0")

# Demo mode check
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

# Geocoding cache to avoid repeated API calls
geocoding_cache: Dict[str, Dict[str, float]] = {}

async def get_coordinates(city: str) -> Dict[str, float]:
    """Get coordinates for a city using Open-Meteo Geocoding API"""
    if city in geocoding_cache:
        return geocoding_cache[city]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en", "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                raise ValueError(f"City '{city}' not found")
            
            result = data["results"][0]
            coords = {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result["name"],
                "country": result.get("country", "")
            }
            geocoding_cache[city] = coords
            return coords
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get coordinates: {str(e)}")

async def get_weather_data(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """Get weather forecast from Open-Meteo API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
                    "timezone": "auto",
                    "forecast_days": days
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")

def interpret_weather_code(code: int, lang: str = "en") -> str:
    """Interpret WMO weather code"""
    weather_codes = {
        "en": {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
            55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
            96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        },
        "zh": {
            0: "晴朗", 1: "大部晴朗", 2: "多云", 3: "阴天",
            45: "有雾", 48: "雾凇", 51: "小毛毛雨", 53: "中毛毛雨",
            55: "大毛毛雨", 61: "小雨", 63: "中雨", 65: "大雨",
            71: "小雪", 73: "中雪", 75: "大雪", 77: "米雪",
            80: "小阵雨", 81: "中阵雨", 82: "强阵雨",
            85: "小阵雪", 86: "大阵雪", 95: "雷暴",
            96: "雷暴伴有小冰雹", 99: "雷暴伴有大冰雹"
        },
        "ja": {
            0: "快晴", 1: "ほぼ晴れ", 2: "一部曇り", 3: "曇り",
            45: "霧", 48: "着氷性の霧", 51: "弱い霧雨", 53: "中程度の霧雨",
            55: "強い霧雨", 61: "弱い雨", 63: "中程度の雨", 65: "強い雨",
            71: "弱い雪", 73: "中程度の雪", 75: "強い雪", 77: "霧雪",
            80: "弱いにわか雨", 81: "中程度のにわか雨", 82: "激しいにわか雨",
            85: "弱いにわか雪", 86: "強いにわか雪", 95: "雷雨",
            96: "雷雨と小ひょう", 99: "雷雨と大ひょう"
        }
    }
    
    lang_codes = weather_codes.get(lang, weather_codes["en"])
    return lang_codes.get(code, "Unknown" if lang == "en" else "未知" if lang == "zh" else "不明")

def get_demo_weather(city: str, days: int = 7, lang: str = "en") -> Dict[str, Any]:
    """Return demo weather data"""
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
    """Return A2A agent card for discovery"""
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "weather_agent",
        "demo_mode": DEMO_MODE
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute a weather-related task"""
    try:
        if request.skill == "get_weather_info":
            # Get weather information for a city
            city = request.params.get("city")
            days = request.params.get("days", 7)
            lang = request.params.get("language", "en")
            
            if not city:
                raise ValueError("City parameter is required")
            
            if DEMO_MODE:
                result = get_demo_weather(city, days, lang)
            else:
                # Get coordinates
                coords = await get_coordinates(city)
                
                # Get weather data
                weather_data = await get_weather_data(
                    coords["latitude"],
                    coords["longitude"],
                    days
                )
                
                # Format response
                daily = weather_data["daily"]
                forecast = []
                for i in range(len(daily["time"])):
                    forecast.append({
                        "date": daily["time"][i],
                        "temperature_max": daily["temperature_2m_max"][i],
                        "temperature_min": daily["temperature_2m_min"][i],
                        "precipitation": daily["precipitation_sum"][i],
                        "weather": interpret_weather_code(daily["weathercode"][i], lang),
                        "wind_speed": daily["windspeed_10m_max"][i]
                    })
                
                summaries = {
                    "en": f"Weather forecast for {coords['name']}, {coords['country']}: {len(forecast)} days",
                    "zh": f"{coords['name']}, {coords['country']} 天气预报: 未来 {len(forecast)} 天",
                    "ja": f"{coords['name']}, {coords['country']} の天気予報: {len(forecast)} 日間"
                }
                
                result = {
                    "city": coords["name"],
                    "country": coords["country"],
                    "forecast": forecast,
                    "summary": summaries.get(lang, summaries["en"])
                }
            
            return TaskResponse(status="success", result=result)
        
        elif request.skill == "check_weather_suitability":
            # Check if weather is suitable for travel
            city = request.params.get("city")
            days = request.params.get("days", 7)
            lang = request.params.get("language", "en")
            
            if not city:
                raise ValueError("City parameter is required")
            
            if DEMO_MODE:
                weather_info = get_demo_weather(city, days, lang)
            else:
                coords = await get_coordinates(city)
                weather_data = await get_weather_data(coords["latitude"], coords["longitude"], days)
                
                daily = weather_data["daily"]
                forecast = []
                for i in range(len(daily["time"])):
                    forecast.append({
                        "date": daily["time"][i],
                        "temperature_max": daily["temperature_2m_max"][i],
                        "temperature_min": daily["temperature_2m_min"][i],
                        "precipitation": daily["precipitation_sum"][i],
                        "weather": interpret_weather_code(daily["weathercode"][i], lang),
                        "wind_speed": daily["windspeed_10m_max"][i]
                    })
                
                weather_info = {
                    "city": coords["name"],
                    "country": coords["country"],
                    "forecast": forecast
                }
            
            # Analyze suitability
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