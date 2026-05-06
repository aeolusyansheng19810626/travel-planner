---
title: Travel Planner
emoji: ✈️
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# ✈️ Travel Planner

An AI-powered travel planning system using multi-agent architecture with LangGraph orchestration and A2A (Agent-to-Agent) protocol.

## 🌟 Features

- **Multi-Agent System**: Weather, Attraction, and Itinerary agents working together
- **LangGraph Orchestration**: Intelligent workflow management with state machines
- **A2A Protocol**: Standardized agent communication and discovery
- **Natural Language Processing**: Powered by Groq LLM
- **Real-time Weather**: Open-Meteo API integration (no API key required)
- **Smart Search**: Tavily API for attraction recommendations
- **Multi-language UI**: Support for English, Chinese, and Japanese
- **Docker Deployment**: Single container with Supervisor process management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI (Port 7860)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Orchestrator (LangGraph + FastAPI)             │
│                        Port 8000                            │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────▼──────────┐
│   Weather   │  │   Attraction    │  │   Itinerary     │
│    Agent    │  │     Agent       │  │     Agent       │
│  Port 8001  │  │   Port 8002     │  │   Port 8003     │
│             │  │                 │  │                 │
│ Open-Meteo  │  │  Tavily API     │  │   Groq LLM      │
└─────────────┘  └─────────────────┘  └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API Key ([Get it here](https://console.groq.com/keys))
- Tavily API Key ([Get it here](https://tavily.com/))

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd travel-planner
```

2. **Create virtual environment**
```bash
# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Start the services**

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

6. **Access the UI**
Open your browser and navigate to: http://localhost:7860

### Docker Deployment

1. **Build the image**
```bash
docker build -t travel-planner .
```

2. **Run the container**
```bash
docker run -p 7860:7860 \
  -e GROQ_API_KEY=your_groq_key \
  -e TAVILY_API_KEY=your_tavily_key \
  travel-planner
```

### HuggingFace Spaces Deployment

1. Create a new Space on HuggingFace
2. Select "Docker" as the SDK
3. Push this repository to the Space
4. Add secrets in Space settings:
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`

## 📖 Usage Examples

### Example Queries

- "Plan a 3-day trip to Tokyo"
- "2 days in Osaka, love history and food"
- "1 day in Kyoto, how's the weather?"
- "5-day romantic trip to Paris"
- "4 days in New York for shopping and food"

### API Endpoints

**Orchestrator (Port 8000)**
- `POST /query` - Natural language query
- `POST /plan` - Structured planning request
- `GET /agents` - List discovered agents
- `GET /health` - Health check

**Weather Agent (Port 8001)**
- `POST /tasks` - Execute weather tasks
- `GET /.well-known/agent.json` - Agent card
- `GET /health` - Health check

**Attraction Agent (Port 8002)**
- `POST /tasks` - Execute attraction tasks
- `GET /.well-known/agent.json` - Agent card
- `GET /health` - Health check

**Itinerary Agent (Port 8003)**
- `POST /tasks` - Execute itinerary tasks
- `GET /.well-known/agent.json` - Agent card
- `GET /health` - Health check

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | LangGraph | Workflow state management |
| Agents | FastAPI | HTTP services |
| Communication | A2A Protocol | Agent discovery & interaction |
| UI | Streamlit | User interface |
| LLM | Groq | Natural language processing |
| Weather | Open-Meteo | Weather data (free, no key) |
| Search | Tavily | Attraction search |
| Deployment | Docker + Supervisor | Process management |

## 📁 Project Structure

```
travel-planner/
├── app.py                          # Streamlit UI
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── Dockerfile                      # Docker configuration
├── supervisord.conf               # Process management
├── start.sh / start.bat           # Local startup scripts
│
├── orchestrator/
│   ├── main.py                    # FastAPI service
│   ├── graph.py                   # LangGraph workflow
│   └── agent_card.json            # A2A agent card
│
└── agents/
    ├── weather_agent/
    │   ├── main.py                # Weather service
    │   └── agent_card.json        # Agent metadata
    │
    ├── attraction_agent/
    │   ├── main.py                # Attraction service
    │   └── agent_card.json        # Agent metadata
    │
    └── itinerary_agent/
        ├── main.py                # Itinerary service
        └── agent_card.json        # Agent metadata
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional
DEMO_MODE=false                    # Set to "true" for demo without API keys
GROQ_MODEL=llama-3.3-70b-versatile # LLM model to use
```

### Port Configuration

- **7860**: Streamlit UI (HuggingFace Spaces requirement)
- **8000**: Orchestrator
- **8001**: Weather Agent
- **8002**: Attraction Agent
- **8003**: Itinerary Agent

## 🧪 Testing

### Health Checks

```bash
# Check orchestrator
curl http://localhost:8000/health

# Check weather agent
curl http://localhost:8001/health

# Check attraction agent
curl http://localhost:8002/health

# Check itinerary agent
curl http://localhost:8003/health
```

### Test Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Tokyo"}'
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Made with ❤️ by Bob

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [Groq](https://groq.com/) - Fast LLM inference
- [Open-Meteo](https://open-meteo.com/) - Free weather API
- [Tavily](https://tavily.com/) - AI search API
- [Streamlit](https://streamlit.io/) - UI framework

---

**Note**: This project demonstrates a multi-agent architecture using modern AI tools and protocols. It's designed for educational purposes and can be extended with additional agents and capabilities.