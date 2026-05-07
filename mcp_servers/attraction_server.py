from typing import Dict, Any, List, Optional, Tuple
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP
from groq import AsyncGroq
from tavily import TavilyClient

load_dotenv(Path(__file__).parent.parent / ".env")

mcp = FastMCP(name="Attraction MCP Server")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b"
]

tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def clean_attractions_with_llm(raw_results: List[Dict[str, Any]], city: str, language: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    if not groq_client or not raw_results:
        return raw_results, None

    lang_name = "English"
    if language == "zh":
        lang_name = "Chinese"
    elif language == "ja":
        lang_name = "Japanese"

    prompt = f"""
You are a travel assistant. Here are raw search results for attractions in {city}.
Extract 5-8 real tourist attractions.

CRITICAL: The JSON keys MUST always be in English: "attractions", "name", "description".
Only the values should be in {lang_name}.

For each attraction provide:
- "name": the attraction name (in {lang_name} or romanized)
- "description": one concise sentence in {lang_name}

Raw data:
{json.dumps(raw_results, ensure_ascii=False)}

Return ONLY this exact JSON structure (keys in English, values in {lang_name}):
{{
  "attractions": [
    {{"name": "...", "description": "..."}}
  ]
}}
"""
    content = None
    used_model = None
    errors = []
    for model in MODELS:
        try:
            response = await groq_client.chat.completions.create(
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

    if not content:
        print(f"All attraction cleanup models failed: {'; '.join(errors)}")
        return raw_results, None

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[attraction_server] JSON parse failed ({e}). Content: {content[:300]}")
        return raw_results, used_model

    cleaned = [item for item in data.get("attractions", []) if item.get("name") and item.get("description")]
    if not cleaned:
        print(f"[attraction_server] No valid cleaned attractions. Keys returned: {list(data.keys())}, data: {str(data)[:300]}")
        return raw_results, used_model

    for item in cleaned:
        item_name = item.get("name", "").lower()
        for raw in raw_results:
            raw_name = raw.get("name", "").lower()
            if item_name in raw_name or raw_name in item_name:
                if raw.get("url"):
                    item["url"] = raw["url"]
                if raw.get("score") is not None:
                    item["score"] = raw["score"]
                break

    return cleaned, used_model

@mcp.tool()
async def search_attractions(
    city: str,
    preferences: Optional[List[str]] = None,
    max_results: int = 5,
    language: str = "en"
) -> Dict[str, Any]:
    """Search tourist attractions using Tavily and clean the results with Groq."""
    if not tavily_client:
        raise RuntimeError("Tavily client not initialized")

    query = f"top tourist attractions in {city}"
    if preferences:
        query += f" {' '.join(preferences)}"
    if language == "zh":
        query += " 请用中文返回景点名称和详细描述"
    elif language == "ja":
        query += " 観光スポット名と説明を日本語で返してください"

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results
    )
    raw_results = [
        {
            "name": result.get("title", "Unknown"),
            "description": result.get("content", ""),
            "url": result.get("url", ""),
            "score": result.get("score", 0)
        }
        for result in response.get("results", [])
    ]
    attractions, model_used = await clean_attractions_with_llm(raw_results, city, language)

    return {
        "city": city,
        "preferences": preferences or [],
        "attractions": attractions,
        "count": len(attractions),
        "model_used": model_used
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8011)
