from typing import Dict, Any, List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP
from groq import Groq

load_dotenv(Path(__file__).parent.parent / ".env")

mcp = FastMCP(name="LLM MCP Server")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant"
]

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def build_language_rules(language: str, days: int) -> str:
    if language == "zh":
        return f"""
输出要求：
- 必须全程使用简体中文回答，不要切换成英文。
- 必须包含第1天到第{days}天，不要提前结束。
- 每天只使用四个时间段：上午、午餐、下午、晚上。
- 每个时间段只写一句简短的话。
- 不要使用 Markdown 表格或 HTML 标签。
- 每句只写地点/活动，最多加一个实用提醒。
- 不要写长描述、地址、价格区间、预订建议或多段小贴士。
"""
    if language == "ja":
        return f"""
出力条件：
- 必ず日本語で回答し、英語に切り替えないでください。
- 1日目から{days}日目まで必ず含め、途中で終わらないでください。
- 各日は午前、昼食、午後、夜の4枠だけにしてください。
- 各時間帯は短い1文だけにしてください。
- Markdownの表やHTMLタグは使わないでください。
- 長い説明、住所、価格帯、予約案内、複数段落のヒントは不要です。
"""
    return f"""
Hard requirements:
- You must answer entirely in English.
- You must include every day from Day 1 through Day {days}; do not stop early.
- For each day, use only these four time slots: Morning, Lunch, Afternoon, Evening.
- Each time slot should be exactly one short sentence.
- Do not use Markdown tables or HTML tags.
- Do not include long descriptions, addresses, price ranges, booking advice, or multi-paragraph tips.
"""

@mcp.tool()
async def generate_itinerary(
    city: str,
    days: int = 3,
    language: str = "en",
    preferences: Optional[List[str]] = None,
    weather_info: Optional[Dict[str, Any]] = None,
    attractions: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Generate a concise travel itinerary using Groq."""
    if not groq_client:
        raise RuntimeError("Groq client not initialized")

    if language == "zh":
        system = "你是一位专业旅行规划师，请生成简洁、实用、适合演示的旅行行程。"
        context = f"为 {city} 创建 {days} 天旅行行程。\n\n"
        if preferences:
            context += f"用户偏好：{'、'.join(preferences)}\n\n"
        context += "天气预报：\n"
        if weather_info and weather_info.get("forecast"):
            for index, item in enumerate(weather_info["forecast"][:days], 1):
                context += f"第{index}天：{item.get('weather', 'N/A')}，{item.get('temperature_max', 'N/A')}°C / {item.get('temperature_min', 'N/A')}°C\n"
        context += "\n推荐景点：\n"
    elif language == "ja":
        system = "あなたはプロの旅行プランナーです。簡潔で実用的なデモ向け旅行プランを作成してください。"
        context = f"{city}の{days}日間の旅行プランを作成してください。\n\n"
        if preferences:
            context += f"ユーザーの好み：{'、'.join(preferences)}\n\n"
        context += "天気予報：\n"
        if weather_info and weather_info.get("forecast"):
            for index, item in enumerate(weather_info["forecast"][:days], 1):
                context += f"{index}日目：{item.get('weather', 'N/A')}、{item.get('temperature_max', 'N/A')}°C / {item.get('temperature_min', 'N/A')}°C\n"
        context += "\nおすすめ観光スポット：\n"
    else:
        system = "You are a professional travel planner. Create a concise, practical demo itinerary."
        context = f"Create a {days}-day travel itinerary for {city}.\n\n"
        if preferences:
            context += f"User preferences: {', '.join(preferences)}\n\n"
        context += "Weather forecast:\n"
        if weather_info and weather_info.get("forecast"):
            for index, item in enumerate(weather_info["forecast"][:days], 1):
                context += f"Day {index}: {item.get('weather', 'N/A')}, {item.get('temperature_max', 'N/A')}°C / {item.get('temperature_min', 'N/A')}°C\n"
        context += "\nRecommended attractions:\n"

    for attr in (attractions or [])[:10]:
        context += f"- {attr.get('name', 'Unknown')}: {attr.get('description', 'N/A')}\n"
    context += "\n" + build_language_rules(language, days)

    response = None
    model_used = None
    errors = []
    for model in MODELS:
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=3500
            )
            model_used = model
            break
        except Exception as e:
            print(f"Model {model} failed: {e}, trying next...")
            errors.append(f"{model}: {str(e)}")

    if not response:
        raise RuntimeError(f"All models failed. Details: {'; '.join(errors)}")

    return {
        "city": city,
        "days": days,
        "language": language,
        "preferences": preferences or [],
        "itinerary_text": response.choices[0].message.content,
        "weather_considered": weather_info is not None,
        "attractions_included": len(attractions) if attractions else 0,
        "model_used": model_used
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8012)
