---
title: Travel Planner
emoji: ✈️
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# ✈️ 旅行规划助手

基于多智能体架构的AI旅行规划系统，使用LangGraph编排和A2A（Agent-to-Agent）协议。

## 🌟 特性

- **多智能体系统**：天气、景点和行程智能体协同工作
- **LangGraph编排**：使用状态机进行智能工作流管理
- **A2A协议**：标准化的智能体通信和发现机制
- **自然语言处理**：由大语言模型驱动
- **实时天气**：集成Open-Meteo API（无需API密钥）
- **智能搜索**：使用Tavily API进行景点推荐
- **多语言界面**：支持英文、中文和日文
- **Docker部署**：单容器Supervisor进程管理

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit UI (端口 7860)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│           Orchestrator (LangGraph + FastAPI)                │
│                        端口 8000                            │
└──────┬──────────────────┬──────────────────┬────────────────┘
       │                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌──────▼──────────┐
│   天气      │  │    景点         │  │    行程         │
│   智能体    │  │   智能体        │  │   智能体        │
│  端口 8001  │  │  端口 8002      │  │  端口 8003      │
│             │  │                 │  │                 │
│ Open-Meteo  │  │  Tavily API     │  │   LLM           │
└─────────────┘  └─────────────────┘  └─────────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- 大语言模型 API密钥 (例如 GROQ)
- Tavily API密钥 ([获取地址](https://tavily.com/))

### 本地开发

1. **克隆仓库**
```bash
git clone <repository-url>
cd travel-planner
```

2. **创建虚拟环境**
```bash
# 创建venv
python -m venv venv

# 激活 (Linux/Mac)
source venv/bin/activate

# 激活 (Windows)
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件并添加你的API密钥
```

5. **启动服务**

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

6. **访问界面**
在浏览器中打开：http://localhost:7860

### Docker部署

1. **构建镜像**
```bash
docker build -t travel-planner .
```

2. **运行容器**
```bash
docker run -p 7860:7860 \
  -e GROQ_API_KEY=你的groq密钥 \
  -e TAVILY_API_KEY=你的tavily密钥 \
  travel-planner
```

### HuggingFace Spaces部署

1. 在HuggingFace上创建新Space
2. 选择"Docker"作为SDK
3. 将此仓库推送到Space
4. 在Space设置中添加密钥：
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`

## 📖 使用示例

### 示例查询

- "帮我规划东京3天旅行"
- "大阪2天，喜欢历史和美食"
- "京都1天，天气好吗？"
- "巴黎5天浪漫之旅"
- "纽约4天购物和美食"

### API端点

**Orchestrator (端口 8000)**
- `POST /query` - 自然语言查询
- `POST /plan` - 结构化规划请求
- `GET /agents` - 列出已发现的智能体
- `GET /health` - 健康检查

**天气智能体 (端口 8001)**
- `POST /tasks` - 执行天气任务
- `GET /.well-known/agent.json` - 智能体卡片
- `GET /health` - 健康检查

**景点智能体 (端口 8002)**
- `POST /tasks` - 执行景点任务
- `GET /.well-known/agent.json` - 智能体卡片
- `GET /health` - 健康检查

**行程智能体 (端口 8003)**
- `POST /tasks` - 执行行程任务
- `GET /.well-known/agent.json` - 智能体卡片
- `GET /health` - 健康检查

## 🛠️ 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 编排 | LangGraph | 工作流状态管理 |
| 智能体 | FastAPI | HTTP服务 |
| 通信 | A2A协议 | 智能体发现与交互 |
| 界面 | Streamlit | 用户界面 |
| LLM | 大语言模型 | 自然语言处理 |
| 天气 | Open-Meteo | 天气数据（免费，无需密钥）|
| 搜索 | Tavily | 景点搜索 |
| 部署 | Docker + Supervisor | 进程管理 |

## 📁 项目结构

```
travel-planner/
├── app.py                          # Streamlit界面
├── requirements.txt                # Python依赖
├── .env.example                    # 环境变量模板
├── Dockerfile                      # Docker配置
├── supervisord.conf               # 进程管理
├── start.sh / start.bat           # 本地启动脚本
│
├── orchestrator/
│   ├── main.py                    # FastAPI服务
│   ├── graph.py                   # LangGraph工作流
│   └── agent_card.json            # A2A智能体卡片
│
└── agents/
    ├── weather_agent/
    │   ├── main.py                # 天气服务
    │   └── agent_card.json        # 智能体元数据
    │
    ├── attraction_agent/
    │   ├── main.py                # 景点服务
    │   └── agent_card.json        # 智能体元数据
    │
    └── itinerary_agent/
        ├── main.py                # 行程服务
        └── agent_card.json        # 智能体元数据
```

## 🔧 配置

### 环境变量

```bash
# 必需
GROQ_API_KEY=你的groq_api密钥
TAVILY_API_KEY=你的tavily_api密钥

# 可选
DEMO_MODE=false                    # 设为"true"可在无API密钥时演示
```

### 端口配置

- **7860**: Streamlit界面（HuggingFace Spaces要求）
- **8000**: Orchestrator
- **8001**: 天气智能体
- **8002**: 景点智能体
- **8003**: 行程智能体

## 🧪 测试

### 健康检查

```bash
# 检查orchestrator
curl http://localhost:8000/health

# 检查天气智能体
curl http://localhost:8001/health

# 检查景点智能体
curl http://localhost:8002/health

# 检查行程智能体
curl http://localhost:8003/health
```

### 测试查询

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "帮我规划东京3天旅行"}'
```

## 🎯 工作流程

1. **用户输入**：通过Streamlit界面输入自然语言查询
2. **查询解析**：Orchestrator使用LangGraph解析目的地、天数和偏好
3. **并行调用**：
   - 天气智能体获取天气预报
   - 景点智能体搜索推荐景点
4. **行程生成**：行程智能体基于天气和景点数据生成详细行程
5. **结果展示**：在界面上展示完整的旅行计划

## 🤝 贡献

欢迎贡献！请随时提交Pull Request。

## 📄 许可证

MIT许可证 - 详见LICENSE文件

## 👨‍💻 作者

由Bob用❤️制作

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 工作流编排
- [Groq](https://groq.com/) - 快速LLM推理
- [Open-Meteo](https://open-meteo.com/) - 免费天气API
- [Tavily](https://tavily.com/) - AI搜索API
- [Streamlit](https://streamlit.io/) - UI框架

---

**注意**：本项目展示了使用现代AI工具和协议的多智能体架构。它专为教育目的设计，可以扩展更多智能体和功能。
