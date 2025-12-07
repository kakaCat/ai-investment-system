# AI功能设置指南

> 本系统AI功能使用指南 - 支持本地模型（Ollama）和DeepSeek API

---

## 🎯 快速开始

### 方式1: 本地模型（推荐，免费）⭐

**优势**:
- ✅ 完全免费，无需API Key
- ✅ 数据隐私安全（本地运行）
- ✅ 无网络限制，响应快速
- ✅ 支持中文优化模型（Qwen 2.5）

**步骤**:

#### 1. 安装Ollama

**Mac/Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**:
下载安装包: https://ollama.com/download/windows

#### 2. 下载推荐模型

```bash
# 推荐: Qwen 2.5 7B（中文优化，7GB）
ollama pull qwen2.5:7b

# 或者更大的14B模型（更强性能，需要16GB内存）
ollama pull qwen2.5:14b

# 或者使用Llama 3（英文更强）
ollama pull llama3:8b
```

#### 3. 运行模型

```bash
# 启动模型服务（默认端口11434）
ollama serve

# 或者直接运行模型（会自动启动服务）
ollama run qwen2.5:7b
```

#### 4. 测试连接

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 测试生成
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "分析一下茅台股票",
  "stream": false
}'
```

#### 5. 启动后端服务

```bash
cd /Users/mac/Documents/ai/stock
./scripts/dev.sh
```

**完成！** AI功能现在使用本地模型，无需配置API Key。

---

### 方式2: DeepSeek API（云端，性价比高）

**优势**:
- ✅ 无需本地算力
- ✅ 性价比高（比GPT便宜95%）
- ✅ 支持超长上下文（64K tokens）
- ✅ 中文优化

**步骤**:

#### 1. 获取API Key

访问: https://platform.deepseek.com/

1. 注册账号
2. 进入API管理
3. 创建API Key
4. 充值（最低10元）

#### 2. 配置环境变量

编辑 `backend/.env` 文件:

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7
```

#### 3. 启动服务

```bash
./scripts/dev.sh
```

**完成！** 系统会自动检测API Key并使用DeepSeek API。

---

## 🔍 AI功能选择逻辑

系统会按以下顺序自动选择AI后端：

```
1. 检测本地Ollama（http://localhost:11434）
   ↓ 可用？
   ├─ Yes → 使用本地模型（免费）
   └─ No → 继续

2. 检测DeepSeek API Key
   ↓ 已配置？
   ├─ Yes → 使用DeepSeek API
   └─ No → 返回Mock数据（提示配置）
```

**查看当前使用的AI后端**:
```bash
# 查看后端日志
tail -f scripts/logs/backend.log

# 调用AI API时会显示:
# "Using Ollama local model: qwen2.5:7b"
# 或
# "Using DeepSeek API"
```

---

## 📊 AI功能列表

### 1. 单股AI分析

**API**: `POST /api/v1/ai/single-analysis`

**功能**: 对单只股票进行全面AI分析（基本面+技术面+估值）

**响应示例**:
```json
{
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
    "holding_period": "6-12个月",
    "stop_loss_price": 85.0
  },
  "ai_reasons": [
    "财务状况良好，ROE持续增长",
    "技术面形成上升趋势",
    "估值处于合理区间"
  ],
  "confidence_level": 78.5
}
```

### 2. AI对话

**API**: `POST /api/v1/ai/chat/message/send`

**功能**: 与AI投资顾问对话，支持上下文股票

**特性**:
- 支持多轮对话
- 自动保存对话历史
- 可关联特定股票上下文

### 3. 批量AI分析

**API**: `POST /api/v1/ai/daily-analysis/create`

**功能**: 批量分析多只股票（适合每日复盘）

**状态**: 当前同步执行，后续将集成Celery异步任务

### 4. 每日复盘

**API**: `POST /api/v1/ai/review/generate`

**功能**: 基于持仓和重要事件生成每日复盘报告

**状态**: 框架完成，等待实时数据源集成

---

## 🛠️ 高级配置

### 切换模型

**本地Ollama - 在代码中指定**:

编辑 `backend/app/utils/ai_client.py:45`:
```python
if not model:
    model = "qwen2.5:14b"  # 改为14B模型
    # model = "llama3:8b"  # 或使用Llama 3
```

**DeepSeek - 在环境变量中配置**:

编辑 `backend/.env`:
```bash
DEEPSEEK_MODEL=deepseek-chat  # 默认
# DEEPSEEK_MODEL=deepseek-coder  # 代码专用模型
```

### 调整温度参数

温度控制AI输出的随机性（0-1）:
- 0.3: 更保守、确定性强
- **0.7**: 默认，平衡
- 0.9: 更有创造性

```bash
# .env文件
DEEPSEEK_TEMPERATURE=0.7
```

### 调整Token限制

```bash
# .env文件
DEEPSEEK_MAX_TOKENS=4000  # 单次最大token数
```

---

## 🐛 故障排查

### 问题1: Ollama连接失败

**症状**: 返回Mock数据，提示"请配置本地模型或DeepSeek API"

**检查**:
```bash
# 1. Ollama是否运行
curl http://localhost:11434/api/tags

# 2. 检查进程
ps aux | grep ollama

# 3. 重启Ollama
pkill ollama
ollama serve
```

### 问题2: 模型下载慢

**解决**: 使用国内镜像（如有）

```bash
# 或者直接下载模型文件到~/.ollama/models/
```

### 问题3: DeepSeek API调用失败

**检查**:
1. API Key是否正确
2. 账户余额是否充足
3. 网络是否可访问api.deepseek.com

```bash
# 测试API Key
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### 问题4: 响应速度慢

**本地模型优化**:
- 使用更小的模型（qwen2.5:7b → qwen2.5:3b）
- 使用GPU加速（需NVIDIA显卡）
```bash
# 安装GPU版本Ollama
ollama pull qwen2.5:7b
OLLAMA_GPU=1 ollama serve
```

**DeepSeek API**:
- 减少max_tokens
- 调低temperature

---

## 📈 性能对比

| 模型 | 响应速度 | 内存占用 | 成本 | 中文能力 | 推荐场景 |
|------|---------|---------|------|---------|---------|
| **Qwen 2.5 7B** | 2-5秒 | 8GB | 免费 | ⭐⭐⭐⭐⭐ | 默认推荐 |
| Qwen 2.5 14B | 5-10秒 | 16GB | 免费 | ⭐⭐⭐⭐⭐ | 高性能服务器 |
| Llama 3 8B | 2-5秒 | 8GB | 免费 | ⭐⭐⭐ | 英文为主 |
| **DeepSeek API** | 1-3秒 | - | ¥0.001/1K tokens | ⭐⭐⭐⭐⭐ | 云端部署 |

**成本估算**（DeepSeek API）:
- 单股分析：约2000 tokens = ￥0.002
- 对话回复：约500 tokens = ￥0.0005
- 每日复盘：约3000 tokens = ￥0.003

10元约可分析5000只股票或进行20000轮对话。

---

## 📚 相关文档

- [Ollama官方文档](https://github.com/ollama/ollama)
- [Qwen 2.5模型](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [DeepSeek API文档](https://platform.deepseek.com/api-docs/)
- [项目AI架构设计](../design/architecture/ai-integration.md)

---

**最后更新**: 2025-11-20
**维护者**: AI Team
