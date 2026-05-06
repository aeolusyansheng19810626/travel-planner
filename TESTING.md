# 🧪 Testing Guide - Travel Planner

This guide helps you test the Travel Planner system step by step.

## Prerequisites

Before testing, ensure you have:
- ✅ Python 3.11+ installed
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ `.env` file configured with API keys
- ✅ All services running

## Quick Health Check

### 1. Check All Services

Run these commands to verify all services are running:

```bash
# Orchestrator
curl http://localhost:8000/health

# Weather Agent
curl http://localhost:8001/health

# Attraction Agent
curl http://localhost:8002/health

# Itinerary Agent
curl http://localhost:8003/health
```

Expected response for each:
```json
{
  "status": "healthy",
  "agent": "agent_name",
  ...
}
```

### 2. Check Agent Discovery

```bash
curl http://localhost:8000/agents
```

Expected response:
```json
{
  "count": 3,
  "agents": {
    "weather_agent": {...},
    "attraction_agent": {...},
    "itinerary_agent": {...}
  }
}
```

## Individual Agent Testing

### Weather Agent

**Test 1: Get Weather Info**
```bash
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "get_weather_info",
    "params": {
      "city": "Tokyo",
      "days": 3
    }
  }'
```

**Test 2: Check Weather Suitability**
```bash
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "check_weather_suitability",
    "params": {
      "city": "Paris",
      "days": 5
    }
  }'
```

### Attraction Agent

**Test 1: Search Attractions**
```bash
curl -X POST http://localhost:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "search_attractions",
    "params": {
      "city": "Kyoto",
      "preferences": ["historical", "culture"],
      "max_results": 5
    }
  }'
```

**Test 2: Recommend Attractions**
```bash
curl -X POST http://localhost:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "recommend_attractions",
    "params": {
      "city": "Osaka",
      "preferences": ["food"],
      "days": 2
    }
  }'
```

### Itinerary Agent

**Test: Create Itinerary**
```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "create_itinerary",
    "params": {
      "city": "Tokyo",
      "days": 3,
      "preferences": ["historical", "food"]
    }
  }'
```

## End-to-End Testing

### Test 1: Simple Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Tokyo"}'
```

### Test 2: Query with Preferences

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "2 days in Osaka, love history and food"}'
```

### Test 3: Structured Plan

```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Kyoto",
    "days": 1,
    "preferences": ["historical", "nature"]
  }'
```

## UI Testing

### 1. Access the UI

Open your browser and navigate to: http://localhost:7860

### 2. Test Language Switching

- Switch between English, Chinese (中文), and Japanese (日本語)
- Verify all UI elements update correctly

### 3. Test Example Queries

Click on the example query buttons in the sidebar:
- ✅ "Plan a 3-day trip to Tokyo"
- ✅ "2 days in Osaka, love history and food"
- ✅ "1 day in Kyoto, how's the weather?"

### 4. Test Custom Queries

Enter your own queries in the chat input:
- "5-day romantic trip to Paris"
- "4 days in New York for shopping and food"
- "3-day historical tour of Rome"

### 5. Verify Results Display

Check that the response includes:
- ✅ Destination, days, and preferences
- ✅ Weather information (expandable)
- ✅ Attractions list (expandable)
- ✅ Detailed itinerary (expandable)
- ✅ Processing messages (expandable)

## Demo Mode Testing

If you don't have API keys, test in demo mode:

1. Set `DEMO_MODE=true` in `.env`
2. Restart services
3. All agents will return demo data
4. Verify the system works end-to-end with demo data

## Common Issues & Solutions

### Issue 1: Orchestrator Can't Find Agents

**Symptom:** `"agents_discovered": 0`

**Solution:**
1. Check if all agent services are running
2. Wait 3-5 seconds after starting agents before starting orchestrator
3. Check agent ports (8001, 8002, 8003) are not in use

### Issue 2: Weather Agent Returns Error

**Symptom:** `"Failed to get coordinates"`

**Solution:**
1. Check internet connection
2. Verify city name is correct
3. Try a major city name (e.g., "Tokyo", "Paris", "London")

### Issue 3: Attraction Agent Returns Empty Results

**Symptom:** `"attractions": []`

**Solution:**
1. If not in demo mode, verify `TAVILY_API_KEY` is set
2. Check Tavily API quota
3. Try a different city or preferences

### Issue 4: Itinerary Agent Fails

**Symptom:** `"Itinerary generation failed"`

**Solution:**
1. Verify `GROQ_API_KEY` is set correctly
2. Check Groq API quota
3. Try with demo mode to verify system works

### Issue 5: UI Shows "Orchestrator Offline"

**Symptom:** Red status in sidebar

**Solution:**
1. Verify orchestrator is running on port 8000
2. Check orchestrator logs for errors
3. Restart orchestrator service

## Performance Testing

### Response Time Benchmarks

Expected response times (approximate):

- **Weather Agent**: 1-3 seconds
- **Attraction Agent**: 2-5 seconds (with Tavily API)
- **Itinerary Agent**: 3-8 seconds (with LLM generation)
- **Full Query**: 10-20 seconds (sequential workflow)

### Load Testing

For production deployment, test with multiple concurrent requests:

```bash
# Install Apache Bench
# Ubuntu: sudo apt-get install apache2-utils
# Mac: brew install ab

# Test with 10 concurrent requests
ab -n 10 -c 2 -p query.json -T application/json http://localhost:8000/query
```

Where `query.json` contains:
```json
{"query": "Plan a 3-day trip to Tokyo"}
```

## Automated Testing Script

Create a test script `test_all.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Travel Planner System"
echo "================================"

# Test health endpoints
echo "1. Testing health endpoints..."
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .

# Test agent discovery
echo "2. Testing agent discovery..."
curl -s http://localhost:8000/agents | jq '.count'

# Test end-to-end query
echo "3. Testing end-to-end query..."
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Plan a 3-day trip to Tokyo"}' | jq '.status'

echo "✅ All tests completed!"
```

Run with: `chmod +x test_all.sh && ./test_all.sh`

## Success Criteria

Your system is working correctly if:

- ✅ All 4 health checks return `"status": "healthy"`
- ✅ Agent discovery finds 3 agents
- ✅ Individual agent tests return successful responses
- ✅ End-to-end queries complete within 20 seconds
- ✅ UI displays all components correctly
- ✅ Multi-language switching works
- ✅ Demo mode works without API keys

## Next Steps

After successful testing:

1. **Deploy to Production**: Use Docker or HuggingFace Spaces
2. **Monitor Performance**: Set up logging and monitoring
3. **Add More Agents**: Extend with hotel, restaurant, or transport agents
4. **Improve LLM Prompts**: Fine-tune prompts for better itineraries
5. **Add Caching**: Cache weather and attraction data to reduce API calls

---

**Need Help?** Check the main README.md or open an issue on GitHub.