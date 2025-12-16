# 🚀 快速启动指南

> AI投资管理系统 - 5分钟上手

---

## 📋 前置要求

### 必需环境
```bash
✅ Python 3.11+
✅ Node.js 18+
✅ PostgreSQL 15+
✅ Git
```

### 可选环境
```bash
⭐ Docker (可选，用于数据库)
⭐ Redis (可选，用于缓存)
```

---

## ⚡ 一键启动 (推荐)

### 1. 克隆项目
```bash
git clone <repository-url>
cd ai-investment-system
```

### 2. 启动开发环境
```bash
./scripts/dev.sh
```

就这么简单! 🎉

脚本会自动:
- ✅ 启动后端 (http://localhost:8000)
- ✅ 启动前端 (http://localhost:5175)
- ✅ 自动重载代码变更
- ✅ 记录日志到 `scripts/logs/`

### 3. 访问应用

```
前端: http://localhost:5175
后端: http://localhost:8000
API文档: http://localhost:8000/docs
```

### 4. 停止服务

```bash
./scripts/stop.sh
```

---

## 🔧 手动启动 (可选)

### 后端启动

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入:
# - DATABASE_URL
# - DEEPSEEK_API_KEY
# - TUSHARE_API_KEY

# 3. 数据库迁移
alembic upgrade head

# 4. 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev

# 访问: http://localhost:5175
```

---

## 🎯 功能体验

### 1. AI单股分析

```
步骤:
1. 登录系统
2. 进入 "持仓管理" 或 "股票搜索"
3. 点击任意股票进入详情页
4. 点击 "🤖 AI分析" 按钮
5. 等待30秒，查看AI分析结果

结果包含:
- 综合评分 (0-100)
- 基本面/技术面/估值评分
- AI投资建议
- 置信度
```

### 2. AI对话

```
方式1: 从股票详情进入
1. 股票详情页 → AI分析 → "💬 与AI对话"
2. 输入问题: "现在适合加仓吗？"
3. 查看AI回复

方式2: 独立页面
1. 左侧菜单 → 💬 AI对话
2. 输入通用问题: "什么是价值投资？"
3. 查看AI回复
```

### 3. 批量分析

```
1. 选择多只股票
2. 点击 "批量分析"
3. 查看分析进度
4. 查看所有股票评分
5. 导出CSV报告
```

### 4. 每日复盘

```
1. 左侧菜单 → 📊 每日复盘
2. 查看:
   - 市场总结
   - 持仓表现
   - 重要事件
   - 明日预测
3. 导出报告
```

---

## 🔑 API密钥配置

### 1. DeepSeek API (必需)

```bash
# 获取方式:
1. 访问: https://platform.deepseek.com/
2. 注册账号
3. 创建API Key

# 配置:
export DEEPSEEK_API_KEY="your-api-key"
```

### 2. Tushare API (可选)

```bash
# 获取方式:
1. 访问: https://tushare.pro/
2. 注册账号
3. 获取Token

# 配置:
export TUSHARE_API_KEY="your-token"
```

**说明**: 没有Tushare时会使用AkShare作为备选数据源

---

## 📊 数据库配置

### 使用Docker (推荐)

```bash
# 启动PostgreSQL
docker run -d \
  --name ai-investment-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_investment \
  -p 5432:5432 \
  postgres:15

# 数据库URL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_investment
```

### 本地安装

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Linux
sudo apt install postgresql-15
sudo systemctl start postgresql

# 创建数据库
createdb ai_investment
```

---

## 🧪 开发工具

### 架构检查

```bash
python scripts/check_architecture.py
```

输出:
```
✅ 架构检查通过！
所有代码符合架构规范。
```

### 前端Lint

```bash
cd frontend
npm run lint
```

### 前端构建

```bash
cd frontend
npm run build

# 输出: dist/
```

### 后端测试

```bash
cd backend
pytest

# 指定文件
pytest tests/unit/backend/test_ai.py
```

---

## 🐛 常见问题

### 1. 端口已被占用

```bash
# 查看端口占用
lsof -i :8000  # 后端
lsof -i :5175  # 前端

# 杀掉进程
kill -9 <PID>

# 或修改端口
# 前端: frontend/vite.config.ts
# 后端: ./scripts/dev.sh (修改端口参数)
```

### 2. 数据库连接失败

```bash
# 检查PostgreSQL状态
pg_isready

# 检查数据库是否存在
psql -l | grep ai_investment

# 重新创建数据库
dropdb ai_investment
createdb ai_investment
cd backend
alembic upgrade head
```

### 3. AI API调用失败

```bash
# 检查API Key
echo $DEEPSEEK_API_KEY

# 测试API连接
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"

# 检查网络代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### 4. 前端依赖安装失败

```bash
# 清理缓存
rm -rf node_modules
rm package-lock.json

# 重新安装
npm install

# 或使用镜像
npm install --registry=https://registry.npmmirror.com
```

### 5. 后端依赖冲突

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 重新安装
pip install -r requirements.txt
```

---

## 📚 进阶配置

### 1. 环境变量完整列表

```bash
# backend/.env

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_investment

# AI服务
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 数据源
TUSHARE_API_KEY=your-tushare-token

# JWT密钥
SECRET_KEY=your-secret-key-here

# 环境
ENVIRONMENT=development

# 日志级别
LOG_LEVEL=INFO
```

### 2. 前端代理配置

```typescript
// frontend/vite.config.ts

export default defineConfig({
  server: {
    port: 5175,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 3. CORS配置

```python
# backend/app/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎓 学习资源

### 项目文档
- [CLAUDE.md](CLAUDE.md) - 项目开发指南 ⭐
- [后端架构约束](backend/ARCHITECTURE.md)
- [前端架构约束](frontend/ARCHITECTURE.md)
- [数据库设计](docs/design/database/schema-v1.md)
- [PRD v3.1](docs/prd/v3/main.md)

### 技术文档
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Vue 3官方文档](https://vuejs.org/)
- [Element Plus文档](https://element-plus.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)

### API文档
- [DeepSeek API](https://platform.deepseek.com/docs)
- [Tushare文档](https://tushare.pro/document/2)
- [AkShare文档](https://akshare.akfamily.xyz/)

---

## 🤝 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 开发功能

```bash
# 启动开发环境
./scripts/dev.sh

# 编辑代码...
# 实时预览: http://localhost:5175
```

### 3. 测试验证

```bash
# 架构检查
python scripts/check_architecture.py

# 前端Lint
cd frontend && npm run lint

# 后端测试
cd backend && pytest
```

### 4. 提交代码

```bash
git add .
git commit -m "feat(module): add feature description"
git push origin feature/your-feature-name
```

### 5. 创建PR

```bash
# 使用GitHub CLI
gh pr create --title "Feature: xxx" --body "Description..."

# 或通过Web界面创建
```

---

## 💡 快速提示

### VSCode推荐插件

```json
{
  "recommendations": [
    "Vue.volar",              // Vue 3支持
    "dbaeumer.vscode-eslint", // ESLint
    "esbenp.prettier-vscode", // Prettier
    "ms-python.python",       // Python
    "ms-python.vscode-pylance" // Python类型提示
  ]
}
```

### 快捷命令

```bash
# 查看日志
tail -f scripts/logs/backend.log
tail -f scripts/logs/frontend.log

# 快速重启
./scripts/stop.sh && ./scripts/dev.sh

# 数据库重置
cd backend
alembic downgrade base
alembic upgrade head

# 清理构建
rm -rf frontend/dist
rm -rf backend/__pycache__
```

---

## 📞 获取帮助

### 项目问题
- 查看 [CLAUDE.md](CLAUDE.md)
- 查看 [文档](docs/)
- 提交 Issue

### 技术支持
- FastAPI: [GitHub Discussions](https://github.com/tiangolo/fastapi/discussions)
- Vue: [Discord](https://chat.vuejs.org/)
- Element Plus: [GitHub Issues](https://github.com/element-plus/element-plus/issues)

---

## 🎉 开始使用

现在你已经掌握了所有启动知识，开始体验吧！

```bash
# 一键启动
./scripts/dev.sh

# 访问应用
open http://localhost:5175
```

Happy Coding! 🚀

---

**文档版本**: v1.0
**最后更新**: 2025-12-08
