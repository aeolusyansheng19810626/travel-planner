import streamlit as st
import requests
from datetime import datetime
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Page configuration
st.set_page_config(
    page_title="Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Orchestrator endpoint
ORCHESTRATOR_URL = "http://localhost:8000"

# Demo mode check
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Language state initialization
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Multi-language translations
i18n = {
    "zh": {
        "title": "✈️ 旅行规划助手",
        "subtitle": "基于AI的智能旅行规划系统",
        "system_status": "系统状态",
        "discovered_agents": "已发现的代理",
        "example_queries": "💡 示例查询",
        "refresh_status": "🔄 刷新",
        "clear_history": "🗑️ 清除历史",
        "orchestrator_online": "🟢 协调器在线",
        "orchestrator_offline": "🔴 协调器离线",
        "orchestrator_offline_msg": "❌ 协调器离线。请先启动服务。",
        "weather_agent": "天气代理",
        "attraction_agent": "景点代理",
        "itinerary_agent": "行程代理",
        "weather_agent_desc": "提供天气预报和旅行适宜性分析",
        "attraction_agent_desc": "搜索和推荐旅游景点",
        "itinerary_agent_desc": "生成详细的旅行行程",
        "description_label": "描述",
        "endpoint_label": "端点",
        "skills_label": "技能",
        "example_1": "帮我规划东京3天旅行",
        "example_2": "大阪2天，喜欢历史和美食",
        "example_3": "京都1天，天气好吗？",
        "example_4": "巴黎5天浪漫之旅",
        "example_5": "纽约4天购物和美食",
        "example_6": "罗马3天历史文化之旅",
        "chat_input_placeholder": "输入您的旅行计划需求...",
        "agent_label": "代理",
        "skill_label": "技能",
        "demo_mode": "演示模式",
        "processing": "处理中...",
        "destination": "目的地",
        "days": "天数",
        "preferences": "偏好",
        "weather_info": "天气信息",
        "attractions": "景点推荐",
        "itinerary": "行程安排",
        "error": "错误",
        "messages": "处理消息",
    },
    "ja": {
        "title": "✈️ 旅行プランナー",
        "subtitle": "AIベースのスマート旅行計画システム",
        "system_status": "システムステータス",
        "discovered_agents": "検出されたエージェント",
        "example_queries": "💡 サンプルクエリ",
        "refresh_status": "🔄 更新",
        "clear_history": "🗑️ 履歴をクリア",
        "orchestrator_online": "🟢 オーケストレータオンライン",
        "orchestrator_offline": "🔴 オーケストレータオフライン",
        "orchestrator_offline_msg": "❌ オーケストレータがオフラインです。サービスを起動してください。",
        "weather_agent": "天気エージェント",
        "attraction_agent": "観光スポットエージェント",
        "itinerary_agent": "旅程エージェント",
        "weather_agent_desc": "天気予報と旅行適性分析を提供",
        "attraction_agent_desc": "観光スポットを検索・推薦",
        "itinerary_agent_desc": "詳細な旅行日程を生成",
        "description_label": "説明",
        "endpoint_label": "エンドポイント",
        "skills_label": "スキル",
        "example_1": "東京3日間の旅行を計画して",
        "example_2": "大阪2日間、歴史と美食が好き",
        "example_3": "京都1日、天気はどう？",
        "example_4": "パリ5日間ロマンチック旅行",
        "example_5": "ニューヨーク4日間ショッピングとグルメ",
        "example_6": "ローマ3日間歴史文化の旅",
        "chat_input_placeholder": "旅行計画のご要望を入力...",
        "agent_label": "エージェント",
        "skill_label": "スキル",
        "demo_mode": "デモモード",
        "processing": "処理中...",
        "destination": "目的地",
        "days": "日数",
        "preferences": "好み",
        "weather_info": "天気情報",
        "attractions": "観光スポット",
        "itinerary": "旅程",
        "error": "エラー",
        "messages": "処理メッセージ",
    },
    "en": {
        "title": "✈️ Travel Planner",
        "subtitle": "AI-Powered Smart Travel Planning System",
        "system_status": "System Status",
        "discovered_agents": "Discovered Agents",
        "example_queries": "💡 Example Queries",
        "refresh_status": "🔄 Refresh",
        "clear_history": "🗑️ Clear History",
        "orchestrator_online": "🟢 Orchestrator Online",
        "orchestrator_offline": "🔴 Orchestrator Offline",
        "orchestrator_offline_msg": "❌ Orchestrator is offline. Please start the services first.",
        "weather_agent": "Weather Agent",
        "attraction_agent": "Attraction Agent",
        "itinerary_agent": "Itinerary Agent",
        "weather_agent_desc": "Provides weather forecasts and travel suitability analysis",
        "attraction_agent_desc": "Searches and recommends tourist attractions",
        "itinerary_agent_desc": "Generates detailed travel itineraries",
        "description_label": "Description",
        "endpoint_label": "Endpoint",
        "skills_label": "Skills",
        "example_1": "Plan a 3-day trip to Tokyo",
        "example_2": "2 days in Osaka, love history and food",
        "example_3": "1 day in Kyoto, how's the weather?",
        "example_4": "5-day romantic trip to Paris",
        "example_5": "4 days in New York for shopping and food",
        "example_6": "3-day historical tour of Rome",
        "chat_input_placeholder": "Enter your travel planning request...",
        "agent_label": "Agent",
        "skill_label": "Skill",
        "demo_mode": "Demo Mode",
        "processing": "Processing...",
        "destination": "Destination",
        "days": "Days",
        "preferences": "Preferences",
        "weather_info": "Weather Info",
        "attractions": "Attractions",
        "itinerary": "Itinerary",
        "error": "Error",
        "messages": "Processing Messages",
    }
}

def t(key: str) -> str:
    """Get translation for current language"""
    return i18n[st.session_state.lang].get(key, key)

def check_orchestrator_health():
    """Check if orchestrator is online"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_agents():
    """Get list of discovered agents"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/agents", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def send_query(query: str):
    """Send query to orchestrator"""
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/query",
            json={"query": query},
            timeout=120
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title(t("title"))
    st.caption(t("subtitle"))
    
    # Language selector
    lang_options = {"English": "en", "中文": "zh", "日本語": "ja"}
    selected_lang = st.selectbox(
        "Language / 语言 / 言語",
        options=list(lang_options.keys()),
        index=list(lang_options.values()).index(st.session_state.lang)
    )
    st.session_state.lang = lang_options[selected_lang]
    
    st.divider()
    
    # System status
    st.subheader(t("system_status"))
    
    col1, col2 = st.columns([3, 1])
    with col1:
        orchestrator_online = check_orchestrator_health()
        if orchestrator_online:
            st.success(t("orchestrator_online"))
        else:
            st.error(t("orchestrator_offline"))
    with col2:
        if st.button(t("refresh_status")):
            st.rerun()
    
    if DEMO_MODE:
        st.info(f"🎭 {t('demo_mode')}")
    
    # Discovered agents
    if orchestrator_online:
        st.divider()
        st.subheader(t("discovered_agents"))
        
        agents_data = get_agents()
        if agents_data and agents_data.get("agents"):
            for agent_name, agent_info in agents_data["agents"].items():
                with st.expander(f"🤖 {agent_info.get('name', agent_name)}"):
                    st.write(f"**{t('description_label')}:** {agent_info.get('description', 'N/A')}")
                    st.write(f"**{t('endpoint_label')}:** {agent_info.get('endpoint', 'N/A')}")
                    if agent_info.get('skills'):
                        st.write(f"**{t('skills_label')}:**")
                        for skill in agent_info['skills']:
                            st.write(f"- {skill.get('name', 'N/A')}")
    
    st.divider()
    
    # Example queries
    st.subheader(t("example_queries"))
    examples = [
        t("example_1"),
        t("example_2"),
        t("example_3"),
        t("example_4"),
        t("example_5"),
        t("example_6")
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": example})
            with st.spinner(t("processing")):
                response = send_query(example)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.divider()
    
    if st.button(t("clear_history"), use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title(t("title"))

if not orchestrator_online:
    st.error(t("orchestrator_offline_msg"))
    st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            # Display assistant response
            response = message["content"]
            if response.get("status") == "success":
                result = response.get("result", {})
                models_used = result.get("models_used") or response.get("models_used") or {}
                if models_used:
                    model_text = ", ".join(f"{step}: {model}" for step, model in models_used.items())
                    st.caption(f"Models used: {model_text}")
                
                # Display destination and days
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t("destination"), result.get("destination", "N/A"))
                with col2:
                    st.metric(t("days"), result.get("days", "N/A"))
                with col3:
                    prefs = result.get("preferences", [])
                    st.metric(t("preferences"), len(prefs))
                
                # Display weather info
                if result.get("weather"):
                    with st.expander(f"🌤️ {t('weather_info')}", expanded=True):
                        weather = result["weather"]
                        st.write(f"**{weather.get('city', 'N/A')}, {weather.get('country', 'N/A')}**")
                        if weather.get("forecast"):
                            display_days = result.get("days", 3)
                            for day in weather["forecast"][:display_days]:
                                st.write(f"**{day.get('date', 'N/A')}:** {day.get('weather', 'N/A')}, "
                                       f"{day.get('temperature_max', 'N/A')}°C / {day.get('temperature_min', 'N/A')}°C")
                
                # Display attractions
                if result.get("attractions"):
                    with st.expander(f"🏛️ {t('attractions')}", expanded=True):
                        attractions = result["attractions"]
                        for attr in attractions[:5]:  # Show first 5
                            name = attr.get('name', 'Unknown')
                            st.write(f"**{name}**")
                            fallback_descriptions = {
                                "zh": f"{name} 是 {result.get('destination', '当地')} 的热门景点。",
                                "ja": f"{name} は {result.get('destination', '現地')} の人気観光スポットです。",
                                "en": f"{name} is a popular attraction in {result.get('destination', 'the destination')}."
                            }
                            description = (
                                attr.get('description')
                                or attr.get('content')
                                or fallback_descriptions.get(result.get("language", st.session_state.lang), fallback_descriptions["en"])
                            )
                            st.write(description)
                            st.divider()
                
                # Display itinerary
                if result.get("itinerary"):
                    with st.expander(f"📅 {t('itinerary')}", expanded=True):
                        itinerary = result["itinerary"]
                        
                        # Check if it's demo mode format or LLM format
                        if itinerary.get("daily_plans"):
                            # Demo mode format
                            for day_plan in itinerary["daily_plans"]:
                                st.subheader(f"Day {day_plan.get('day', 'N/A')}")
                                if day_plan.get("weather_note"):
                                    st.info(day_plan["weather_note"])
                                for activity in day_plan.get("activities", []):
                                    st.write(f"**{activity.get('time', 'N/A')}** - {activity.get('activity', 'N/A')}")
                                    st.write(activity.get('description', ''))
                                st.divider()
                        elif itinerary.get("itinerary_text"):
                            # LLM format
                            st.write(itinerary["itinerary_text"])
                
                # Display processing messages
                if response.get("messages"):
                    with st.expander(f"📝 {t('messages')}"):
                        for msg in response["messages"]:
                            st.write(f"- {msg}")
            
            elif response.get("status") == "error":
                models_used = response.get("models_used") or {}
                if models_used:
                    model_text = ", ".join(f"{step}: {model}" for step, model in models_used.items())
                    st.caption(f"Models used: {model_text}")
                st.error(f"{t('error')}: {response.get('error', 'Unknown error')}")

# Chat input
if prompt := st.chat_input(t("chat_input_placeholder")):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner(t("processing")):
            response = send_query(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Made with Bob
