from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Tuple
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from groq import Groq

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

app = FastAPI(title="Attraction Agent", version="1.0.0")

# Demo mode check
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Tavily client
tavily_client = None
if not DEMO_MODE and TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Warning: Tavily client initialization failed: {e}")
else:
    print("🔍 Attraction Agent running in DEMO MODE")

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant"
]
groq_client = None
if not DEMO_MODE and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Warning: Groq client initialization failed: {e}")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

def get_demo_attractions(city: str, preferences: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Return demo attraction data"""
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
    
    # Get attractions for the city
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
    
    # Filter by preferences if provided
    if preferences:
        pref_lower = [p.lower() for p in preferences]
        filtered = []
        for attr in attractions:
            if any(pref in attr["category"].lower() or pref in attr["description"].lower() for pref in pref_lower):
                filtered.append(attr)
        if filtered:
            attractions = filtered
    
    return attractions

async def clean_attractions_with_llm(raw_results: List[Dict], city: str, lang: str) -> Tuple[List[Dict], Optional[str]]:
    """Clean and extract attractions using LLM"""
    if not groq_client or not raw_results:
        return raw_results, None
    
    lang_name = "English"
    if lang == "zh": lang_name = "Chinese"
    elif lang == "ja": lang_name = "Japanese"
        
    prompt = f"""
    You are a travel assistant. Here are some raw search results for attractions in {city}.
    Filter out any noise (ads, navigation text, irrelevant info) and extract exactly 5-8 real tourist attractions.
    For each attraction, provide a clean, short name and a one-sentence description in {lang_name}.
    
    Raw data:
    {json.dumps(raw_results, ensure_ascii=False)}
    
    Return ONLY a valid JSON object with an 'attractions' key containing an array of objects with 'name' and 'description' keys.
    {{
      "attractions": [
        {{"name": "...", "description": "..."}}
      ]
    }}
    """
    
    try:
        content = None
        errors = []
        used_model = None
        for model in MODELS:
            try:
                response = groq_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("empty response content")
                used_model = model
                break
            except Exception as e:
                print(f"Model {model} failed during attraction cleanup: {e}, trying next...")
                errors.append(f"{model}: {str(e)}")
                continue

        if not content:
            raise RuntimeError(f"All models failed. Details: {'; '.join(errors)}")

        data = json.loads(content)
        cleaned = data.get("attractions", [])
        cleaned = [
            c for c in cleaned
            if c.get("name") and c.get("description")
        ]
        
        # Merge url and score back if possible
        for c in cleaned:
            c_name = c.get("name", "").lower()
            for r in raw_results:
                if c_name in r.get("name", "").lower() or r.get("name", "").lower() in c_name:
                    if "url" in r: c["url"] = r["url"]
                    if "score" in r: c["score"] = r["score"]
                    if not c.get("description") and r.get("description"):
                        c["description"] = r["description"]
                    break
        
        return (cleaned if cleaned else raw_results), used_model
    except Exception as e:
        print(f"LLM cleaning failed: {e}")
        return raw_results, None

async def search_attractions_tavily(
    city: str,
    preferences: Optional[List[str]] = None,
    max_results: int = 5,
    lang: str = "en"
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Search for attractions using Tavily API"""
    if not tavily_client:
        raise HTTPException(status_code=500, detail="Tavily client not initialized")
    
    try:
        # Build search query
        query = f"top tourist attractions in {city}"
        if preferences:
            query += f" {' '.join(preferences)}"
        
        # Append language instruction for Tavily
        if lang == "zh":
            query += " (请用中文返回景点名称和详细描述)"
        elif lang == "ja":
            query += " (観光スポットの名前と詳細な説明を日本語で提供してください)"
        
        # Search with Tavily
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        # Format raw results
        raw_attractions = []
        for result in response.get("results", []):
            raw_attractions.append({
                "name": result.get("title", "Unknown"),
                "description": result.get("content", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0)
            })
            
        # Clean with LLM
        cleaned_attractions, model_used = await clean_attractions_with_llm(raw_attractions, city, lang)
        
        return cleaned_attractions, model_used
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tavily search failed: {str(e)}")

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
        "agent": "attraction_agent",
        "tavily_connected": tavily_client is not None,
        "demo_mode": DEMO_MODE
    }

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute an attraction-related task"""
    try:
        if request.skill == "search_attractions":
            # Search for attractions in a city
            city = request.params.get("city")
            preferences = request.params.get("preferences", [])
            max_results = request.params.get("max_results", 5)
            lang = request.params.get("language", "en")
            
            if not city:
                raise ValueError("City parameter is required")
            
            if DEMO_MODE or not tavily_client:
                attractions = get_demo_attractions(city, preferences)
                model_used = None
            else:
                attractions, model_used = await search_attractions_tavily(city, preferences, max_results, lang)
            
            result = {
                "city": city,
                "preferences": preferences,
                "attractions": attractions,
                "count": len(attractions),
                "model_used": model_used
            }
            
            return TaskResponse(status="success", result=result)
        
        elif request.skill == "get_attraction_details":
            # Get detailed information about a specific attraction
            attraction_name = request.params.get("attraction_name")
            city = request.params.get("city")
            
            if not attraction_name:
                raise ValueError("Attraction name parameter is required")
            
            if DEMO_MODE or not tavily_client:
                # Return demo details
                result = {
                    "name": attraction_name,
                    "city": city,
                    "description": f"Detailed information about {attraction_name}",
                    "opening_hours": "9:00 AM - 6:00 PM",
                    "admission_fee": "Varies",
                    "tips": ["Visit early to avoid crowds", "Allow 2-3 hours for visit"],
                    "demo_mode": True
                }
            else:
                # Search for specific attraction details
                query = f"{attraction_name} {city} tourist information opening hours admission"
                response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
                
                details = []
                for result in response.get("results", []):
                    details.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", "")
                    })
                
                result = {
                    "name": attraction_name,
                    "city": city,
                    "details": details
                }
            
            return TaskResponse(status="success", result=result)
        
        elif request.skill == "recommend_attractions":
            # Recommend attractions based on user preferences
            city = request.params.get("city")
            preferences = request.params.get("preferences", [])
            days = request.params.get("days", 3)
            
            if not city:
                raise ValueError("City parameter is required")
            
            if DEMO_MODE or not tavily_client:
                all_attractions = get_demo_attractions(city, preferences)
            else:
                all_attractions, _ = await search_attractions_tavily(city, preferences, max_results=10)
            
            # Organize by days
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
            
            result = {
                "city": city,
                "days": days,
                "preferences": preferences,
                "daily_recommendations": daily_recommendations,
                "total_attractions": len(all_attractions)
            }
            
            return TaskResponse(status="success", result=result)
        
        else:
            raise ValueError(f"Unknown skill: {request.skill}")
    
    except Exception as e:
        return TaskResponse(status="error", error=str(e))

# Made with Bob
