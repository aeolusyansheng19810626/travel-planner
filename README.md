---
title: Travel Planner
emoji: ✈️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# Travel Planner

多智能体 AI 旅行规划系统。输入自然语言查询（中文 / 英文 / 日文），三个智能体协同完成天气分析、景点推荐和行程编排，结果实时流式呈现在编辑风格的三栏界面中。

**作者：Sheng Yan**

---

## 界面预览

三栏布局：左侧系统状态与示例查询 · 中间聊天流与输入框 · 右侧完整行程报告（天气 · 景点 · 时间线）

---

## 架构

```
┌──────────────────────────────────────────────────┐
│         React Frontend  (Vite + TypeScript)      │
│         编辑风格 UI · SSE 实时进度 · 三语 i18n   │
└────────────────────┬─────────────────────────────┘
                     │ HTTP + SSE (POST /query/stream)
┌────────────────────▼─────────────────────────────┐
│       Orchestrator  (FastAPI + LangGraph)         │
│       端口 8000 · 同时提供前端静态文件            │
└────┬───────────────┬──────────────────┬───────────┘
     │ A2A           │ A2A              │ A2A
┌────▼────┐    ┌─────▼─────┐    ┌──────▼──────┐
│  天气   │    │   景点    │    │   行程      │
│  Agent  │    │   Agent   │    │   Agent     │
│  :8001  │    │   :8002   │    │   :8003     │
└────┬────┘    └─────┬─────┘    └──────┬──────┘
     │ MCP           │ MCP              │ MCP
┌────▼────┐    ┌─────▼─────┐    ┌──────▼──────┐
│Weather  │    │Attraction │    │   LLM MCP   │
│MCP :8010│    │MCP :8011  │    │   :8012     │
│Open-    │    │Tavily +   │    │   Groq      │
│Meteo    │    │Groq 清洗  │    │             │
└─────────┘    └───────────┘    └─────────────┘
```

**为什么用 MCP 分层？** 智能体不直接调用任何外部 API——API 密钥和 HTTP 调用封装在 MCP Server 层，Agent 只通过 MCP 协议取数据。替换底层数据源（如换掉 Tavily）只需改 MCP Server，Agent 代码无需改动。

---

## 工作流程

1. 用户在界面输入自然语言查询
2. Orchestrator 的 `parse_query` 节点用 LLM 提取目的地（含本地名）、天数、偏好、语言
3. LangGraph 串行执行三个节点，每个节点完成后通过 SSE 推送事件到前端：
   - `parsed` → 前端显示识别到的城市和天数
   - `weather` → 天气智能体拉取 Open-Meteo 预报
   - `attractions` → 景点智能体搜索 Tavily 并用 LLM 清洗
   - `itinerary` → 行程智能体调用 LLM 生成多天时间线
   - `done` → 前端渲染完整行程报告
4. 任意单个智能体失败时降级渲染，不中断整体流程

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vite · React 18 · TypeScript · Tailwind CSS v4 |
| 编排 | FastAPI · LangGraph · SSE 流式输出 |
| 智能体通信 | A2A 协议（HTTP POST /tasks） |
| 工具封装 | FastMCP（MCP Server） |
| LLM | Groq（llama-4-scout · llama-3.1 · qwen3，自动降级） |
| 天气数据 | Open-Meteo（免费，无需密钥） |
| 景点搜索 | Tavily API |
| 部署 | Docker multi-stage build · Supervisor 进程管理 |

---

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Groq API Key（[免费申请](https://console.groq.com/)）
- Tavily API Key（[免费申请](https://tavily.com/)）

### 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/aeolusyansheng19810626/travel-planner.git
cd travel-planner

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 GROQ_API_KEY 和 TAVILY_API_KEY

# 3. 安装 Python 依赖
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. 安装并构建前端
cd frontend && npm install && npm run build && cd ..

# 5. 启动所有服务
./start.sh        # Linux / Mac
start.bat         # Windows
```

访问 **http://localhost:8000**

> 前端开发模式（热更新）：在 `frontend/` 目录下运行 `npm run dev`，访问 http://localhost:5173

### Docker

```bash
docker build -t travel-planner .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  travel-planner
```

### HuggingFace Spaces

1. Fork 本仓库到 HuggingFace Space（Docker SDK）
2. 在 Space Settings → Secrets 中添加：
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`
3. 推送即自动构建并部署

---

## 项目结构

```
travel-planner/
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── components/          # BrandBar · LeftRail · ChatColumn
│   │   │                        # ResultPanel · AttrThumb · TweaksPanel
│   │   ├── hooks/useQueryStream.ts  # SSE 流式 hook
│   │   ├── lib/
│   │   │   ├── adapters.ts      # 后端响应 → TripData 适配层
│   │   │   ├── context.tsx      # 全局状态（React Context）
│   │   │   └── i18n.ts          # zh / en / ja 三语字典
│   │   └── styles/tokens.css    # 设计 token（颜色 · 字体 · 间距）
│   ├── vite.config.ts
│   └── package.json
│
├── orchestrator/
│   ├── main.py                  # FastAPI · POST /query/stream (SSE)
│   │                            # · 静态文件服务（生产环境）
│   ├── graph.py                 # LangGraph 四节点工作流
│   └── llm_client.py            # Groq 客户端（多模型自动降级）
│
├── agents/
│   ├── weather_agent/           # 天气智能体（端口 8001）
│   ├── attraction_agent/        # 景点智能体（端口 8002）
│   └── itinerary_agent/         # 行程智能体（端口 8003）
│
├── mcp_servers/
│   ├── weather_server.py        # Open-Meteo 封装（端口 8010）
│   ├── attraction_server.py     # Tavily 封装（端口 8011）
│   └── llm_server.py            # Groq 封装（端口 8012）
│
├── Dockerfile                   # multi-stage：Node 构建 + Python 运行
├── supervisord.conf             # 进程管理（8 个服务）
├── requirements.txt
└── start.sh / start.bat
```

---

## 环境变量

```bash
GROQ_API_KEY=...        # 必需：LLM 推理
TAVILY_API_KEY=...      # 必需：景点搜索
DEMO_MODE=false         # 可选：设为 true 时使用内置 fixture 数据（无需 API）
```

---

## API 端点

| 端点 | 说明 |
|---|---|
| `POST /query/stream` | SSE 流式查询（前端使用） |
| `POST /query` | 一次性查询（返回完整 JSON） |
| `GET /agents` | 列出已发现的智能体 |
| `GET /health` | 健康检查 |

---

## 示例查询

```
# 中文
帮我规划东京 3 天旅行
北京 2 天，风景名胜
大阪 2 天，关注美食

# English
Plan a 3-day trip to Paris focusing on culture
New York 4 days, shopping and food

# 日本語
京都 1 日、天気はどう？
札幌 1 日、グルメ
```

---

## 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) — 工作流编排
- [Groq](https://groq.com/) — 快速 LLM 推理
- [Open-Meteo](https://open-meteo.com/) — 免费天气 API
- [Tavily](https://tavily.com/) — AI 搜索 API
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP Server 框架
