# 部署配置

> 部署、监控、运维配置和脚本

---

## 📂 目录结构

```
deploy/
├── README.md              # 本文件 - 部署总览
├── docker/                # Docker配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── nginx/                 # Nginx配置
│   ├── nginx.conf
│   └── ssl/               # SSL证书
└── scripts/               # 部署脚本
    ├── deploy.sh          # 一键部署
    ├── backup.sh          # 数据备份
    └── rollback.sh        # 回滚脚本
```

---

## 🚀 部署方式

### 1. 本地开发环境

```bash
# 使用开发脚本
./scripts/dev.sh

# 服务地址
# - 后端: http://localhost:8000
# - 前端: http://localhost:5175
# - API文档: http://localhost:8000/docs
```

### 2. Docker部署

```bash
# 构建镜像
docker-compose -f deploy/docker/docker-compose.yml build

# 启动服务
docker-compose -f deploy/docker/docker-compose.yml up -d

# 查看日志
docker-compose -f deploy/docker/docker-compose.yml logs -f
```

### 3. 生产环境部署

```bash
# 执行部署脚本
./deploy/scripts/deploy.sh production

# 流程：
# 1. 备份数据库
# 2. 拉取最新代码
# 3. 构建镜像
# 4. 数据库迁移
# 5. 重启服务
# 6. 健康检查
```

---

## 🐳 Docker配置

### 后端镜像 (Dockerfile.backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端镜像 (Dockerfile.frontend)

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

---

## 🌐 环境配置

### 本地环境 (local)
- 数据库: 本地 PostgreSQL
- 调试: 开启
- 日志级别: DEBUG

### 测试环境 (staging)
- 数据库: 测试数据库
- 调试: 开启
- 日志级别: INFO

### 生产环境 (production)
- 数据库: 生产数据库
- 调试: 关闭
- 日志级别: WARNING
- HTTPS: 启用

---

## 📊 监控和日志

### ���志位置

```
logs/
├── backend.log           # 后端日志
├── frontend.log          # 前端日志
├── nginx/
│   ├── access.log        # 访问日志
│   └── error.log         # 错误日志
└── deploy.log            # 部署日志
```

### 监控指标

| 指标 | 工具 | 阈值 |
|------|------|------|
| CPU使用率 | Docker stats | < 80% |
| 内存使用率 | Docker stats | < 80% |
| 磁盘使用率 | df -h | < 85% |
| API响应时间 | 日志分析 | P99 < 500ms |
| 数据库连接数 | PostgreSQL | < 80% pool |

---

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        run: ./deploy/scripts/deploy.sh
```

---

## 🔐 安全配置

### 环境变量

```bash
# 必需环境变量
DATABASE_URL=postgresql://...
SECRET_KEY=xxx
DEEPSEEK_API_KEY=xxx

# 可选环境变量
REDIS_URL=redis://...
SENTRY_DSN=https://...
```

### SSL证书

```bash
# 使用 Let's Encrypt
certbot --nginx -d yourdomain.com
```

---

## 🔧 运维脚本

### 备份数据库

```bash
./deploy/scripts/backup.sh
```

### 回滚部署

```bash
./deploy/scripts/rollback.sh
```

### 查看服务状态

```bash
docker-compose ps
```

---

## 📋 部署检查清单

### 部署前
- [ ] 代码已合并到主分支
- [ ] 所有测试通过
- [ ] 数据库迁移脚本准备好
- [ ] 环境变量配置正确
- [ ] 备份当前数据库

### 部署中
- [ ] 拉取最新代码
- [ ] 构建新镜像
- [ ] 执行数据库迁移
- [ ] 重启服务
- [ ] 健康检查通过

### 部署后
- [ ] 验证核心功能
- [ ] 检查日志无错误
- [ ] 监控指标正常
- [ ] 更新部署文档

---

## 🔗 相关文档

- [运维文档](../docs/operations/)
- [数据库设计](../docs/design/database/)
- [开发脚本](../scripts/)

---

**最后更新**: 2025-11-19
**负责人**: DevOps Team
