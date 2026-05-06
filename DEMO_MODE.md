# 🎭 DEMO_MODE 说明文档

## 什么是DEMO_MODE？

`DEMO_MODE` 是一个环境变量开关，允许系统在**没有API密钥**的情况下运行，使用预设的演示数据代替真实API调用。

## 为什么需要DEMO_MODE？

### 1. **快速演示**
- 无需注册API密钥即可展示系统功能
- 适合产品演示、教学、测试

### 2. **开发调试**
- 避免频繁调用API消耗配额
- 加快开发迭代速度
- 不依赖网络连接

### 3. **HuggingFace Spaces部署**
- 公开Space可能不想暴露API密钥
- 允许访客体验系统而不消耗你的API配额

## 如何启用DEMO_MODE？

### 方法1：环境变量文件
在 `.env` 文件中设置：
```bash
DEMO_MODE=true
```

### 方法2：Docker运行时
```bash
docker run -p 7860:7860 \
  -e DEMO_MODE=true \
  travel-planner
```

### 方法3：HuggingFace Spaces
在Space设置中添加环境变量：
- Key: `DEMO_MODE`
- Value: `true`

## DEMO_MODE的工作原理

### 各Agent的行为变化

#### 1. Weather Agent (天气智能体)

**正常模式：**
```python
# 调用Open-Meteo API获取真实天气数据
coords = await get_coordinates("Tokyo")
weather_data = await get_weather_data(coords["latitude"], coords["longitude"])
```

**DEMO模式：**
```python
# 返回预设的演示天气数据
def get_demo_weather(city: str, days: int = 7):
    return {
        "city": city,
        "forecast": [
            {
                "date": "2024-05-06",
                "temperature_max": 25,
                "temperature_min": 15,
                "weather": "Partly cloudy",
                "precipitation": 0.5
            },
            # ... 更多演示数据
        ]
    }
```

#### 2. Attraction Agent (景点智能体)

**正常模式：**
```python
# 调用Tavily API搜索真实景点
response = tavily_client.search(
    query=f"top tourist attractions in {city}",
    search_depth="advanced"
)
```

**DEMO模式：**
```python
# 返回预设的景点数据库
attractions_db = {
    "Tokyo": [
        {
            "name": "Senso-ji Temple",
            "description": "Tokyo's oldest temple...",
            "category": "historical",
            "rating": 4.5
        },
        # ... 更多预设景点
    ]
}
```

#### 3. Itinerary Agent (行程智能体)

**正常模式：**
```python
# 调用Groq LLM生成个性化行程
response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...]
)
```

**DEMO模式：**
```python
# 返回预设的行程模板
def get_demo_itinerary(city, days):
    return {
        "daily_plans": [
            {
                "day": 1,
                "activities": [
                    {
                        "time": "09:00 - 12:00",
                        "activity": "Morning sightseeing",
                        "description": "Explore main attractions"
                    },
                    # ... 更多活动
                ]
            }
        ]
    }
```

## DEMO_MODE vs 正常模式对比

| 特性 | 正常模式 | DEMO模式 |
|------|---------|---------|
| **API密钥** | 必需 | 不需要 |
| **数据来源** | 实时API调用 | 预设演示数据 |
| **网络依赖** | 需要 | 不需要 |
| **响应速度** | 1-10秒 | <1秒 |
| **数据准确性** | 真实数据 | 演示数据 |
| **API配额消耗** | 是 | 否 |
| **适用场景** | 生产环境 | 演示/开发 |

## 演示数据内容

### 预设城市
- **东京 (Tokyo)**: 5个景点（寺庙、塔、市场等）
- **大阪 (Osaka)**: 4个景点（城堡、美食街等）
- **京都 (Kyoto)**: 4个景点（神社、竹林等）
- **其他城市**: 通用景点模板

### 天气数据
- 7天预报
- 温度范围：15-25°C
- 天气状况：晴天、多云、小雨等
- 降水量和风速数据

### 行程模板
- 每天4个时间段
- 包含活动描述和建议
- 考虑天气和景点信息

## 使用建议

### 何时使用DEMO模式？

✅ **推荐使用：**
- 首次安装测试系统
- 产品演示给客户
- 教学和培训
- 开发新功能时
- API配额用完时

❌ **不推荐使用：**
- 生产环境
- 需要真实数据的场景
- 用户期望准确信息时

### 最佳实践

1. **开发阶段**
   ```bash
   # 开发时使用DEMO模式
   DEMO_MODE=true
   ```

2. **测试阶段**
   ```bash
   # 测试时使用真实API
   DEMO_MODE=false
   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key
   ```

3. **生产部署**
   ```bash
   # 生产环境必须使用真实API
   DEMO_MODE=false
   GROQ_API_KEY=production_key
   TAVILY_API_KEY=production_key
   ```

4. **公开演示**
   ```bash
   # HuggingFace Spaces公开演示
   DEMO_MODE=true
   # 不设置API密钥，避免配额被消耗
   ```

## UI中的DEMO模式指示

当DEMO_MODE启用时，UI会显示：
- 侧边栏显示 "🎭 演示模式" / "🎭 Demo Mode"
- 结果中包含 `"demo_mode": true` 标记
- 提醒用户数据为演示数据

## 代码示例

### 检查DEMO模式
```python
import os
from dotenv import load_dotenv

load_dotenv()
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

if DEMO_MODE:
    print("Running in DEMO mode")
else:
    print("Running in PRODUCTION mode")
```

### 条件执行
```python
if DEMO_MODE or not api_client:
    # 使用演示数据
    result = get_demo_data()
else:
    # 调用真实API
    result = await call_real_api()
```

## 常见问题

### Q1: DEMO模式下数据准确吗？
**A:** 不准确。DEMO模式使用预设的演示数据，不反映真实情况。仅用于展示系统功能。

### Q2: 可以部分使用DEMO模式吗？
**A:** 可以。每个Agent独立检查DEMO_MODE，可以只让某些Agent使用演示数据。

### Q3: DEMO模式影响性能吗？
**A:** 反而更快！因为不需要网络API调用，响应速度更快。

### Q4: 如何知道当前是否在DEMO模式？
**A:** 
1. 检查UI侧边栏是否显示"演示模式"
2. 调用 `/health` 端点查看 `"demo_mode"` 字段
3. 查看返回结果中的 `"demo_mode": true` 标记

### Q5: DEMO模式安全吗？
**A:** 是的。DEMO模式不会泄露API密钥，不会消耗API配额，适合公开演示。

## 总结

DEMO_MODE是一个非常实用的功能，它让你可以：
- ✅ 无需API密钥即可运行系统
- ✅ 快速演示系统功能
- ✅ 节省API调用配额
- ✅ 加快开发调试速度
- ✅ 安全地公开部署演示

记住：**DEMO模式用于演示，生产环境请使用真实API！**

---

**Made with ❤️ by Bob**