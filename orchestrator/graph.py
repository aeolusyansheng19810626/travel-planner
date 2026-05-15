from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import httpx
import json
import re
from llm_client import GroqClientWithFallback

class TravelPlanState(TypedDict):
    """State for travel planning workflow"""
    query: str                          # Original user query
    language: str                       # Detected language (en/zh/ja)
    destination: str                    # Parsed destination
    days: int                          # Number of days
    preferences: List[str]             # User preferences
    weather_info: Optional[Dict]       # Weather data from weather agent
    attractions: Optional[List[Dict]]  # Attractions from attraction agent
    itinerary: Optional[Dict]          # Final itinerary from itinerary agent
    models_used: Dict[str, str]        # LLM models used by each step
    messages: List[str]                # Processing messages
    error: Optional[str]               # Error message if any

# Agent endpoints
WEATHER_AGENT_URL = "http://localhost:8001"
ATTRACTION_AGENT_URL = "http://localhost:8002"
ITINERARY_AGENT_URL = "http://localhost:8003"

async def call_agent(url: str, skill: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call an agent via A2A protocol"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{url}/tasks",
                json={"skill": skill, "params": params}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

def detect_language(text: str) -> str:
    """Detect language from text (simple heuristic)"""
    # Check Japanese-specific scripts first (Hiragana, Katakana)
    # Must come before CJK check because kanji appears in both Japanese and Chinese
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return "ja"
    # Check for Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"
    # Default to English
    return "en"

def infer_preferences(text: str) -> List[str]:
    """Infer common travel preferences with simple keyword rules."""
    lowered = text.lower()
    preference_keywords = {
        "romantic": ["romantic", "romance", "浪漫", "ロマンチック"],
        "shopping": ["shopping", "购物", "買い物", "ショッピング"],
        "food": ["food", "gourmet", "美食", "グルメ", "食べ物"],
        "historical": ["history", "historical", "历史", "歷史", "歴史"],
        "culture": ["culture", "cultural", "文化"],
        "nature": ["nature", "自然"],
        "nightlife": ["nightlife", "夜生活", "ナイトライフ"]
    }
    return [
        preference
        for preference, keywords in preference_keywords.items()
        if any(keyword in lowered for keyword in keywords)
    ]

def get_msg(key: str, target_lang: str, **kwargs) -> str:
    """Get translated message"""
    msgs = {
        "parsing": {
            "en": "Parsing user query...",
            "zh": "正在解析用户查询...",
            "ja": "ユーザークエリを解析中..."
        },
        "parsed_info": {
            "en": "Language: {lang}, Destination: {dest}, Days: {days}, Preferences: {prefs}",
            "zh": "语言: {lang}, 目的地: {dest}, 天数: {days}, 偏好: {prefs}",
            "ja": "言語: {lang}, 目的地: {dest}, 日数: {days}, 好み: {prefs}"
        },
        "fetching_weather": {
            "en": "Fetching weather for {dest}...",
            "zh": "正在获取 {dest} 的天气信息...",
            "ja": "{dest} の天気情報を取得中..."
        },
        "weather_success": {
            "en": "Weather data received: {summary}",
            "zh": "已获取天气数据: {summary}",
            "ja": "天気データを取得しました: {summary}"
        },
        "weather_fail": {
            "en": "Weather fetch failed: {error}",
            "zh": "获取天气失败: {error}",
            "ja": "天気情報の取得に失敗しました: {error}"
        },
        "searching_attr": {
            "en": "Searching attractions in {dest}...",
            "zh": "正在搜索 {dest} 的景点...",
            "ja": "{dest} の観光スポットを検索中..."
        },
        "attr_success": {
            "en": "Found {count} attractions",
            "zh": "找到 {count} 个景点",
            "ja": "{count} 件の観光スポットが見つかりました"
        },
        "attr_fail": {
            "en": "Attraction search failed: {error}",
            "zh": "搜索景点失败: {error}",
            "ja": "観光スポットの検索に失敗しました: {error}"
        },
        "generating_itin": {
            "en": "Generating complete itinerary...",
            "zh": "正在生成完整行程...",
            "ja": "完全な旅程を作成中..."
        },
        "itin_success": {
            "en": "Itinerary generated successfully!",
            "zh": "行程生成成功！",
            "ja": "旅程の作成に成功しました！"
        },
        "itin_fail": {
            "en": "Itinerary generation failed: {error}",
            "zh": "行程生成失败: {error}",
            "ja": "旅程の作成に失敗しました: {error}"
        },
        "unrelated": {
            "en": "Sorry, I can only help with travel planning. Please provide a destination and number of days.",
            "zh": "抱歉，我只能帮助规划旅行行程，请输入目的地和天数",
            "ja": "申し訳ありませんが、旅行の計画しかサポートできません。目的地と日数をご入力ください。"
        },
        "missing_dest": {
            "en": "I couldn't identify the destination. Please specify where you want to go.",
            "zh": "我没有识别出目的地，请告诉我你想去哪里。",
            "ja": "目的地が認識できませんでした。どこに行きたいか教えてください。"
        }
    }
    msg_template = msgs.get(key, {}).get(target_lang, msgs.get(key, {}).get("en", key))
    return msg_template.format(**kwargs)

def parse_query(state: TravelPlanState) -> TravelPlanState:
    """Parse user query to extract destination, days, and preferences"""
    query = state["query"].lower()
    original_query = state["query"]
    messages = state.get("messages", [])
    models_used = state.get("models_used", {})
    
    # Detect language
    language = detect_language(original_query)
    messages.append(get_msg("parsing", language))
    
    # Intent Check & Information Extraction
    try:
        from dotenv import load_dotenv
        import os
        from pathlib import Path
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        client = GroqClientWithFallback()
        prompt = f"""
        Analyze the following user query: "{original_query}"

        1. Determine if this is a request for travel planning or related to travel (e.g. "what about AAPL stock" is NOT related).
        2. Extract the destination city (in English, e.g., "Tokyo").
           IMPORTANT — typo & alias correction rules:
           - The user may have typos in Chinese city names. Use context to infer the most likely intended city.
           - Common Chinese typo patterns: 大版→大阪(Osaka), 东京→Tokyo, 巴黎→Paris, 纽约→New York, 首儿→首尔(Seoul).
           - If the query mentions food culture, takoyaki, okonomiyaki, or is paired with "大" + a wrong character, it is very likely Osaka.
           - Prefer well-known tourist cities over obscure cities when the spelling is ambiguous.
        3. Extract the number of days (integer). If not specified, default to 3.
        4. Extract any preferences (e.g., ["historical", "food", "nature", "shopping", "culture", "nightlife"]).

        Respond strictly with only a valid JSON object in this format:
        {{
          "is_travel_query": true/false,
          "destination": "City Name" or null if not found,
          "days": integer,
          "preferences": ["pref1", "pref2"]
        }}
        """

        intent_res = client.chat_completion(
            [
                {
                    "role": "system",
                    "content": "You extract travel-planning intent with typo correction. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        if client.last_model:
            models_used["query_parser"] = client.last_model
        
        if not intent_res:
            raise ValueError("LLM returned None")
            
        import json
        import re
        
        # Use regex to reliably extract JSON object
        json_match = re.search(r'\{.*\}', intent_res, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON object found in response: {intent_res}")
            
        clean_res = json_match.group()
        parsed_data = json.loads(clean_res)
        
        if not parsed_data.get("is_travel_query", True):
            error_msg = get_msg("unrelated", language)
            messages.append(error_msg)
            return {
                **state,
                "error": error_msg,
                "messages": messages
            }
            
        destination = parsed_data.get("destination")
        if not destination or str(destination).lower() == "null" or destination == "":
            error_msg = get_msg("missing_dest", language)
            messages.append(error_msg)
            return {
                **state,
                "error": error_msg,
                "messages": messages
            }
            
        days = parsed_data.get("days")
        if not isinstance(days, int):
            days = 3
            
        preferences = parsed_data.get("preferences", [])
        if not isinstance(preferences, list):
            preferences = []
        inferred_preferences = infer_preferences(original_query)
        preferences = list(dict.fromkeys(preferences + inferred_preferences))
            
    except Exception as e:
        # Stop and return an error if parsing strictly fails, rather than silently defaulting to Tokyo
        error_msg = f"Failed to parse query: {str(e)}"
        messages.append(error_msg)
        return {
            **state,
            "error": error_msg,
            "messages": messages
        }
    
    messages.append(get_msg("parsed_info", language, lang=language, dest=destination, days=days, prefs=preferences))
    
    return {
        **state,
        "language": language,
        "destination": destination,
        "days": days,
        "preferences": preferences,
        "models_used": models_used,
        "messages": messages
    }

async def get_weather(state: TravelPlanState) -> TravelPlanState:
    """Get weather information from weather agent"""
    messages = state.get("messages", [])
    lang = state.get("language", "en")
    messages.append(get_msg("fetching_weather", lang, dest=state['destination']))
    
    result = await call_agent(
        WEATHER_AGENT_URL,
        "get_weather_info",
        {
            "city": state["destination"],
            "days": state["days"],
            "language": lang
        }
    )
    
    if result.get("status") == "success":
        weather_info = result.get("result")
        summary = weather_info.get('summary', 'N/A') if weather_info else 'N/A'
        messages.append(get_msg("weather_success", lang, summary=summary))
        return {
            **state,
            "weather_info": weather_info,
            "messages": messages
        }
    else:
        messages.append(get_msg("weather_fail", lang, error=result.get('error', 'Unknown error')))
        return {
            **state,
            "messages": messages
        }

async def search_attractions(state: TravelPlanState) -> TravelPlanState:
    """Search for attractions from attraction agent"""
    messages = state.get("messages", [])
    lang = state.get("language", "en")
    messages.append(get_msg("searching_attr", lang, dest=state['destination']))
    
    result = await call_agent(
        ATTRACTION_AGENT_URL,
        "search_attractions",
        {
            "city": state["destination"],
            "preferences": state.get("preferences", []),
            "max_results": state["days"] * 3,  # 3 attractions per day
            "language": lang
        }
    )
    
    if result.get("status") == "success":
        attraction_data = result.get("result")
        attractions = attraction_data.get("attractions", []) if attraction_data else []
        models_used = state.get("models_used", {})
        if attraction_data and attraction_data.get("model_used"):
            models_used["attraction_cleaner"] = attraction_data["model_used"]
        messages.append(get_msg("attr_success", lang, count=len(attractions)))
        return {
            **state,
            "attractions": attractions,
            "models_used": models_used,
            "messages": messages
        }
    else:
        messages.append(get_msg("attr_fail", lang, error=result.get('error', 'Unknown error')))
        return {
            **state,
            "messages": messages
        }

async def generate_itinerary(state: TravelPlanState) -> TravelPlanState:
    """Generate final itinerary from itinerary agent"""
    messages = state.get("messages", [])
    lang = state.get("language", "en")
    messages.append(get_msg("generating_itin", lang))
    
    result = await call_agent(
        ITINERARY_AGENT_URL,
        "create_itinerary",
        {
            "city": state["destination"],
            "days": state["days"],
            "language": state.get("language", "en"),
            "preferences": state.get("preferences", []),
            "weather_info": state.get("weather_info"),
            "attractions": state.get("attractions", [])
        }
    )
    
    if result.get("status") == "success":
        itinerary = result.get("result")
        models_used = state.get("models_used", {})
        if itinerary and itinerary.get("model_used"):
            models_used["itinerary_generator"] = itinerary["model_used"]
        messages.append(get_msg("itin_success", lang))
        return {
            **state,
            "itinerary": itinerary,
            "models_used": models_used,
            "messages": messages
        }
    else:
        error_msg = result.get('error', 'Unknown error')
        messages.append(get_msg("itin_fail", lang, error=error_msg))
        return {
            **state,
            "error": error_msg,
            "messages": messages
        }

def should_continue(state: TravelPlanState) -> str:
    """Only parse_query failure is fatal; downstream agent errors degrade gracefully."""
    if state.get("error"):
        return "end"
    return "continue"

def always_continue(_state: TravelPlanState) -> str:
    """Weather / attractions / itinerary failures are non-fatal — keep going."""
    return "continue"

def create_travel_planner_graph():
    """Create the LangGraph workflow for travel planning"""
    workflow = StateGraph(TravelPlanState)

    workflow.add_node("parse_query", parse_query)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("search_attractions", search_attractions)
    workflow.add_node("generate_itinerary", generate_itinerary)

    workflow.set_entry_point("parse_query")

    # parse_query failure is fatal (no destination → cannot continue)
    workflow.add_conditional_edges("parse_query", should_continue, {"continue": "get_weather", "end": END})
    # downstream agent failures are non-fatal: clear error and continue
    workflow.add_conditional_edges("get_weather", always_continue, {"continue": "search_attractions"})
    workflow.add_conditional_edges("search_attractions", always_continue, {"continue": "generate_itinerary"})
    workflow.add_edge("generate_itinerary", END)

    return workflow.compile()

# Made with Bob
