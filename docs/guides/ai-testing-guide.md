# AI功能测试指南

> 快速测试AI功能是否正常工作

---

## 🎯 前置条件

1. **后端服务已启动**:
```bash
cd /Users/mac/Documents/ai/stock
./scripts/dev.sh
```

2. **AI已配置** (二选一):
   - ✅ Ollama运行中 (`ollama serve`)
   - ✅ DeepSeek API Key已配置

3. **已登录获取Token**

---

## 🧪 测试步骤

### 1. 测试单股AI分析

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/single-analysis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519",
    "analysis_type": "comprehensive",
    "include_fundamentals": true,
    "include_technicals": true,
    "include_valuation": true
  }'
```

**预期响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "decision_id": 1,
    "symbol": "600519",
    "stock_name": "贵州茅台",
    "ai_score": {
      "fundamental_score": 75,
      "technical_score": 68,
      "valuation_score": 82,
      "overall_score": 75
    },
    "ai_suggestion": "建议持有，中长期看好",
    "ai_strategy": {
      "target_price": 120.0,
      "recommended_position": 15.0,
      "risk_level": "medium",
      "holding_period": "6-12个月"
    },
    "ai_reasons": [
      "财务状况良好...",
      "技术面形成上升趋势...",
      "估值处于合理区间..."
    ],
    "confidence_level": 78.5
  }
}
```

**检查点**:
- ✅ `code` 为 0
- ✅ `ai_suggestion` 不是Mock数据提示
- ✅ `ai_reasons` 包含具体分析

---

### 2. 测试AI对话

**步骤1**: 创建会话
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat/session/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_symbol": "600519"
  }'
```

**响应** (记录session_id):
```json
{
  "code": 0,
  "data": {
    "session_id": "uuid-xxx-xxx",
    "context_symbol": "600519"
  }
}
```

**步骤2**: 发送消息
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat/message/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-xxx-xxx",
    "message": "分析一下茅台这只股票的投资价值"
  }'
```

**预期响应**:
```json
{
  "code": 0,
  "data": {
    "role": "assistant",
    "content": "贵州茅台是A股市场的白马股...",
    "timestamp": "2025-11-20T10:00:00"
  }
}
```

**检查点**:
- ✅ 回复内容是真实AI分析，不是Mock
- ✅ 回复包含对茅台的具体分析

---

### 3. 测试批量分析

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/daily-analysis/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbols": ["600519", "000858", "600600"]
  }'
```

**预期响应**:
```json
{
  "code": 0,
  "data": {
    "task_id": "task-uuid",
    "status": "pending",
    "total_stocks": 3
  }
}
```

---

## 🔍 检查AI是否真实调用

### 方法1: 查看日志

```bash
tail -f scripts/logs/backend.log
```

**真实调用日志**:
```
INFO: Using Ollama local model: qwen2.5:7b
INFO: AI response received, length: 1234
```

**Mock数据日志**:
```
WARNING: No AI backend available, using mock data
```

### 方法2: Ollama监控

如果使用本地Ollama:
```bash
# 查看Ollama日志
ollama ps

# 应该看到模型正在运行:
NAME            SIZE    UNTIL
qwen2.5:7b      4.7GB   4 minutes from now
```

### 方法3: 检查响应内容

**真实AI响应特征**:
- 回复内容具体、有逻辑
- 每次调用结果不完全相同（temperature>0）
- 分析理由深入、详细

**Mock数据特征**:
- 返回固定模板内容
- 包含"Mock AI响应"字样
- 提示"请配置本地模型或DeepSeek API"

---

## 🐛 常见问题

### Q1: 返回Mock数据怎么办？

**检查清单**:
1. Ollama是否运行？
```bash
curl http://localhost:11434/api/tags
```

2. 模型是否下载？
```bash
ollama list
```

3. DeepSeek API Key是否配置？
```bash
cat backend/.env | grep DEEPSEEK_API_KEY
```

### Q2: 响应速度很慢（>30秒）

**解决方案**:
- 使用更小的模型: `ollama pull qwen2.5:3b`
- 调低max_tokens: 编辑`backend/.env`
```bash
DEEPSEEK_MAX_TOKENS=1000  # 降低到1000
```

### Q3: AI回复不合理

**可能原因**:
- 温度参数太高 → 调低到0.5
- 模型选择不合适 → 尝试其他模型
- Prompt需要优化 → 查看`app/utils/ai_client.py`

---

## 📊 性能基准

### 本地Ollama (qwen2.5:7b)

| 操作 | 首次调用 | 后续调用 | Token数 |
|------|----------|----------|---------|
| 单股分析 | 8-12秒 | 3-5秒 | ~2000 |
| 对话回复 | 5-8秒 | 2-4秒 | ~500 |
| 批量分析(10只) | 30-50秒 | 20-35秒 | ~15000 |

### DeepSeek API

| 操作 | 平均时长 | Token数 | 成本 |
|------|----------|---------|------|
| 单股分析 | 2-4秒 | ~2000 | ¥0.002 |
| 对话回复 | 1-2秒 | ~500 | ¥0.0005 |
| 批量分析(10只) | 10-15秒 | ~15000 | ¥0.015 |

---

## ✅ 验收标准

AI功能工作正常的标志:

1. **单股分析**:
   - ✅ 返回结构化的评分和建议
   - ✅ 理由具体、有深度
   - ✅ 每次分析结果略有不同

2. **对话功能**:
   - ✅ 能理解上下文（股票代码）
   - ✅ 回复与问题相关
   - ✅ 支持多轮对话

3. **性能**:
   - ✅ 单次调用<10秒（本地模型）
   - ✅ 单次调用<5秒（DeepSeek API）

---

**最后更新**: 2025-11-20
**维护者**: QA Team
