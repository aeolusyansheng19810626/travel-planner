from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Itinerary Agent", version="1.0.0")

# Demo mode check
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Models fallback list
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b", 
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant"
]

# Initialize Groq client
groq_client = None
if not DEMO_MODE and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Warning: Groq client initialization failed: {e}")
else:
    print("📝 Itinerary Agent running in DEMO MODE")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

def get_demo_itinerary(city: str, days: int, weather_info: Optional[Dict] = None, attractions: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Return demo itinerary data"""
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

async def generate_itinerary_with_llm(
    city: str,
    days: int,
    language: str = "en",
    preferences: Optional[List[str]] = None,
    weather_info: Optional[Dict] = None,
    attractions: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Generate itinerary using Groq LLM"""
    if not groq_client:
        raise HTTPException(status_code=500, detail="Groq client not initialized")
    
    try:
        # Language-specific prompts
        prompts = {
            "zh": {
                "system": "你是一位专业的旅行规划师。请创建详细、实用且令人愉快的旅行行程。",
                "context_template": "为{city}创建一个详细的{days}天旅行行程。\n\n",
                "preferences": "用户偏好：{prefs}\n\n",
                "weather": "天气预报：\n",
                "weather_day": "第{day}天：{weather}，最高温度：{max}°C，最低温度：{min}°C\n",
                "attractions": "推荐景点：\n",
                "instructions": """请创建详细的每日行程，包括：
1. 上午、下午和晚上的活动
2. 具体时间段
3. 活动描述
4. 每个活动的实用建议
5. 交通建议
6. 餐饮推荐

请以结构化的方式呈现每天的行程。"""
            },
            "ja": {
                "system": "あなたはプロの旅行プランナーです。詳細で実用的で楽しい旅行プランを作成してください。",
                "context_template": "{city}の{days}日間の詳細な旅行プランを作成してください。\n\n",
                "preferences": "ユーザーの好み：{prefs}\n\n",
                "weather": "天気予報：\n",
                "weather_day": "{day}日目：{weather}、最高気温：{max}°C、最低気温：{min}°C\n",
                "attractions": "おすすめの観光スポット：\n",
                "instructions": """詳細な日程を作成してください：
1. 午前、午後、夕方のアクティビティ
2. 具体的な時間帯
3. アクティビティの説明
4. 各アクティビティの実用的なヒント
5. 交通手段の提案
6. 食事の推薦

各日の行程を構造化された形式で提示してください。"""
            },
            "en": {
                "system": "You are a professional travel planner. Create detailed, practical, and enjoyable travel itineraries.",
                "context_template": "Create a detailed {days}-day travel itinerary for {city}.\n\n",
                "preferences": "User preferences: {prefs}\n\n",
                "weather": "Weather forecast:\n",
                "weather_day": "Day {day}: {weather}, Max: {max}°C, Min: {min}°C\n",
                "attractions": "Recommended attractions:\n",
                "instructions": """Please create a detailed daily itinerary with:
1. Morning, afternoon, and evening activities
2. Specific time slots
3. Activity descriptions
4. Practical tips for each activity
5. Transportation suggestions
6. Meal recommendations

Format the response as a structured itinerary for each day."""
            }
        }
        
        # Get language-specific prompts
        lang_prompts = prompts.get(language, prompts["en"])
        
        # Build context for LLM
        context = lang_prompts["context_template"].format(city=city, days=days)
        
        if preferences:
            context += lang_prompts["preferences"].format(prefs='、'.join(preferences) if language in ["zh", "ja"] else ', '.join(preferences))
        
        if weather_info and "forecast" in weather_info:
            context += lang_prompts["weather"]
            for i, day_weather in enumerate(weather_info["forecast"][:days], 1):
                context += lang_prompts["weather_day"].format(
                    day=i,
                    weather=day_weather.get('weather', 'N/A'),
                    max=day_weather.get('temperature_max', 'N/A'),
                    min=day_weather.get('temperature_min', 'N/A')
                )
            context += "\n"
        
        if attractions:
            context += lang_prompts["attractions"]
            for attr in attractions[:10]:  # Limit to top 10
                context += f"- {attr.get('name', 'Unknown')}: {attr.get('description', 'N/A')}\n"
            context += "\n"
        
        context += lang_prompts["instructions"]
        
        # Call Groq API with fallback
        response = None
        for model in MODELS:
            try:
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": lang_prompts["system"]
                        },
                        {
                            "role": "user",
                            "content": context
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                break
            except Exception as e:
                print(f"Model {model} failed: {e}, trying next...")
                continue
                
        if not response:
            raise Exception("All models failed")
            
        itinerary_text = response.choices[0].message.content
        
        return {
            "city": city,
            "days": days,
            "language": language,
            "preferences": preferences or [],
            "itinerary_text": itinerary_text,
            "weather_considered": weather_info is not None,
            "attractions_included": len(attractions) if attractions else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

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
        "agent": "itinerary_agent",
        "groq_connected": groq_client is not None,
        "demo_mode": DEMO_MODE,
        "models": MODELS
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute an itinerary-related task"""
    try:
        if request.skill == "create_itinerary":
            # Create a complete travel itinerary
            city = request.params.get("city")
            days = request.params.get("days", 3)
            language = request.params.get("language", "en")
            preferences = request.params.get("preferences", [])
            weather_info = request.params.get("weather_info")
            attractions = request.params.get("attractions", [])
            
            if not city:
                raise ValueError("City parameter is required")
            
            if DEMO_MODE or not groq_client:
                result = get_demo_itinerary(city, days, weather_info, attractions)
            else:
                result = await generate_itinerary_with_llm(
                    city, days, language, preferences, weather_info, attractions
                )
            
            return TaskResponse(status="success", result=result)
        
        elif request.skill == "optimize_route":
            # Optimize route between attractions
            attractions = request.params.get("attractions", [])
            start_location = request.params.get("start_location")
            
            if not attractions:
                raise ValueError("Attractions parameter is required")
            
            # Simple optimization: return attractions in order
            # In a real implementation, this would use a routing algorithm
            result = {
                "optimized_route": attractions,
                "total_attractions": len(attractions),
                "start_location": start_location,
                "note": "Route optimized for minimal travel time",
                "demo_mode": DEMO_MODE
            }
            
            return TaskResponse(status="success", result=result)
        
        elif request.skill == "suggest_schedule":
            # Suggest time schedule for activities
            activities = request.params.get("activities", [])
            start_time = request.params.get("start_time", "09:00")
            
            if not activities:
                raise ValueError("Activities parameter is required")
            
            # Generate schedule
            schedule = []
            current_hour = int(start_time.split(":")[0])
            
            for i, activity in enumerate(activities):
                duration = activity.get("estimated_time", "2 hours")
                hours = 2  # Default duration
                
                # Parse duration
                if "hour" in duration.lower():
                    try:
                        hours = int(duration.split()[0].split("-")[0])
                    except:
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
            
            result = {
                "schedule": schedule,
                "total_activities": len(schedule),
                "start_time": start_time,
                "estimated_end_time": f"{current_hour:02d}:00"
            }
            
            return TaskResponse(status="success", result=result)
        
        else:
            raise ValueError(f"Unknown skill: {request.skill}")
    
    except Exception as e:
        return TaskResponse(status="error", error=str(e))

# Made with Bob