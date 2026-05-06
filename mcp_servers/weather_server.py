from typing import Dict, Any
import httpx
from fastmcp import FastMCP

mcp = FastMCP(name="Weather MCP Server")

geocoding_cache: Dict[str, Dict[str, Any]] = {}

WEATHER_CODES = {
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
        0: "晴天", 1: "大部晴朗", 2: "多云", 3: "阴天",
        45: "有雾", 48: "雾凇", 51: "小毛毛雨", 53: "中毛毛雨",
        55: "大毛毛雨", 61: "小雨", 63: "中雨", 65: "大雨",
        71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
        80: "小阵雨", 81: "中阵雨", 82: "强阵雨",
        85: "小阵雪", 86: "大阵雪", 95: "雷暴",
        96: "雷暴伴小冰雹", 99: "雷暴伴大冰雹"
    },
    "ja": {
        0: "快晴", 1: "ほぼ晴れ", 2: "一部曇り", 3: "曇り",
        45: "霧", 48: "着氷性の霧", 51: "弱い霧雨", 53: "中程度の霧雨",
        55: "強い霧雨", 61: "弱い雨", 63: "中程度の雨", 65: "強い雨",
        71: "弱い雪", 73: "中程度の雪", 75: "強い雪", 77: "雪粒",
        80: "弱いにわか雨", 81: "中程度のにわか雨", 82: "激しいにわか雨",
        85: "弱いにわか雪", 86: "強いにわか雪", 95: "雷雨",
        96: "雷雨と小さいひょう", 99: "雷雨と大きいひょう"
    }
}

def interpret_weather_code(code: int, language: str = "en") -> str:
    codes = WEATHER_CODES.get(language, WEATHER_CODES["en"])
    return codes.get(code, "Unknown" if language == "en" else "未知" if language == "zh" else "不明")

async def get_coordinates(city: str) -> Dict[str, Any]:
    if city in geocoding_cache:
        return geocoding_cache[city]

    async with httpx.AsyncClient(timeout=20.0) as client:
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

@mcp.tool
async def get_weather(city: str, days: int = 7, language: str = "en") -> Dict[str, Any]:
    """Get a daily weather forecast for a city using Open-Meteo."""
    coords = await get_coordinates(city)

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max",
                "timezone": "auto",
                "forecast_days": days
            }
        )
        response.raise_for_status()
        weather_data = response.json()

    daily = weather_data["daily"]
    forecast = []
    for i in range(len(daily["time"])):
        forecast.append({
            "date": daily["time"][i],
            "temperature_max": daily["temperature_2m_max"][i],
            "temperature_min": daily["temperature_2m_min"][i],
            "precipitation": daily["precipitation_sum"][i],
            "weather": interpret_weather_code(daily["weathercode"][i], language),
            "wind_speed": daily["windspeed_10m_max"][i]
        })

    summaries = {
        "en": f"Weather forecast for {coords['name']}, {coords['country']}: {len(forecast)} days",
        "zh": f"{coords['name']}, {coords['country']} 天气预报: 未来 {len(forecast)} 天",
        "ja": f"{coords['name']}, {coords['country']} の天気予報: {len(forecast)} 日間"
    }

    return {
        "city": coords["name"],
        "country": coords["country"],
        "forecast": forecast,
        "summary": summaries.get(language, summaries["en"])
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8010)
