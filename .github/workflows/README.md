# GitHub Actions CI/CD配置

> 自动化测试、质量检查和部署流水线

---

## 📋 工作流概览

| 工作流 | 触发条件 | 说明 |
|--------|---------|------|
| [ci.yml](ci.yml) | Push/PR到main/develop | 完整的CI流水线：架构检查、测试、质量扫描 |

---

## 🔄 CI流水线

### 执行顺序

```
1. architecture-check (架构符合性检查)
   ↓
2. [并行执行]
   ├─ backend-tests (后端测试)
   ├─ frontend-tests (前端测试)
   └─ security-scan (安全扫描)
   ↓
3. code-quality (代码质量报告)
   ↓
4. e2e-tests (E2E测试，仅PR)
   ↓
5. build-docker (Docker镜像构建，仅main分支)
```

---

## 🎯 各Job详情

### 1. Architecture Check

**目的**: 确保代码符合架构约束

**检查内容**:
- ✅ 所有API使用POST方法
- ✅ Service文件命名规范
- ✅ Converter/Builder使用@staticmethod
- ✅ Repository无业务逻辑

**执行**: `python scripts/check_architecture.py`

**失败则阻止**: 是

---

### 2. Backend Tests

**目的**: 运行后端测试套件

**执行内容**:
1. 启动PostgreSQL测试数据库
2. 安装Python依赖
3. 运行Linting (flake8 + black)
4. 运行单元测试
5. 运行集成测试
6. 上传覆盖率到Codecov

**环境变量**:
- `DATABASE_URL`: 测试数据库连接
- `SECRET_KEY`: JWT密钥
- `ALGORITHM`: JWT算法

**失败则阻止**: 是

---

### 3. Frontend Tests

**目的**: 运行前端测试套件

**执行内容**:
1. 安装Node.js依赖
2. 运行ESLint
3. 运行TypeScript类型检查
4. 运行单元测试
5. 构建前端项目
6. 上传覆盖率

**失败则阻止**: 部分（测试可失败，但构建必须成功）

---

### 4. E2E Tests

**目的**: 运行端到端UI测试

**触发条件**: 仅在Pull Request时运行

**执行内容**:
1. 启动PostgreSQL
2. 安装Playwright
3. Seed测试数据
4. 启动后端服务
5. 启动前端服务
6. 运行UI自动化测试
7. 上传测试截图

**失败则阻止**: 否（允许失败）

---

### 5. Security Scan

**目的**: 安全漏洞扫描

**扫描内容**:
- Trivy文件系统扫描
- Python依赖漏洞检查（Safety）

**失败则阻止**: 否（报告但不阻止）

---

### 6. Code Quality

**目的**: 代码质量分析

**工具**: SonarCloud

**分析内容**:
- 代码异味
- 技术债务
- 安全热点
- 代码覆盖率

**失败则阻止**: 否

---

### 7. Build Docker

**目的**: 构建Docker镜像

**触发条件**: 仅在push到main分支时

**构建镜像**:
- backend:latest
- frontend:latest

**推送**: 暂时禁用（需配置Docker Hub）

---

## 🔧 本地测试

在提交代码前，建议本地运行测试：

### 架构检查

```bash
python scripts/check_architecture.py
```

### 后端测试

```bash
cd backend

# Linting
flake8 app --max-line-length=120
black --check app

# 单元测试
pytest tests/unit/ --cov=app --cov-report=term

# 集成测试
pytest tests/integration/
```

### 前端测试

```bash
cd frontend

# Linting
npm run lint

# 类型检查
npm run type-check

# 构建
npm run build
```

---

## 📊 状态徽章

在README中添加CI状态徽章：

```markdown
![CI Pipeline](https://github.com/{owner}/{repo}/workflows/CI%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/{owner}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{owner}/{repo})
```

---

## ⚙️ 环境变量配置

需要在GitHub仓库Settings → Secrets配置以下密钥：

### 必需（可选功能）

| 密钥 | 用途 | 是否必需 |
|------|------|---------|
| `DOCKER_USERNAME` | Docker Hub用户名 | 否 |
| `DOCKER_PASSWORD` | Docker Hub密码 | 否 |
| `SONAR_TOKEN` | SonarCloud令牌 | 否 |
| `CODECOV_TOKEN` | Codecov令牌 | 否 |

### 默认（由GitHub提供）

- `GITHUB_TOKEN`: 自动提供，用于访问GitHub API

---

## 🚀 启用CI/CD

### 第1步: 推送配置

```bash
git add .github/workflows/
git commit -m "feat(ci): Add GitHub Actions CI/CD pipeline"
git push origin main
```

### 第2步: 查看执行

访问: `https://github.com/{owner}/{repo}/actions`

### 第3步: 配置保护规则（可选）

在 Settings → Branches → Branch protection rules：

- ✅ Require status checks to pass before merging
  - ✅ architecture-check
  - ✅ backend-tests
  - ✅ frontend-tests
- ✅ Require branches to be up to date before merging
- ✅ Require pull request reviews before merging (1 reviewer)

---

## 📋 CI/CD检查清单

提交代码前确认：

- [ ] 通过架构检查: `python scripts/check_architecture.py`
- [ ] 通过后端Linting: `flake8 app && black --check app`
- [ ] 通过后端测试: `pytest tests/`
- [ ] 通过前端Linting: `npm run lint`
- [ ] 前端类型检查通过: `npm run type-check`
- [ ] 前端构建成功: `npm run build`

---

## 🔍 故障排查

### Job失败处理

1. **查看日志**: 点击失败的Job查看详细日志
2. **本地复现**: 在本地运行相同的命令
3. **检查依赖**: 确保requirements.txt/package.json是最新的
4. **数据库问题**: 检查migrations是否正确

### 常见问题

**Q: 架构检查失败**
```bash
# 本地运行检查
python scripts/check_architecture.py

# 查看具体违规项
```

**Q: 测试超时**
```yaml
# 在ci.yml中增加超时时间
timeout-minutes: 30
```

**Q: 依赖安装失败**
```bash
# 更新依赖缓存
git commit --allow-empty -m "chore: Clear CI cache"
```

---

## 📈 改进计划

### 短期 (已实现)

- [x] 架构符合性检查
- [x] 后端单元测试
- [x] 后端集成测试
- [x] 前端Lint和类型检查
- [x] 安全扫描

### 中期 (待实现)

- [ ] 性能测试集成
- [ ] 视觉回归测试
- [ ] 自动化部署到Staging
- [ ] Slack/钉钉通知

### 长期 (规划中)

- [ ] 蓝绿部署
- [ ] 金丝雀发布
- [ ] 自动回滚
- [ ] 监控和告警集成

---

## 🔗 相关文档

- [后端架构约束](../../backend/ARCHITECTURE.md)
- [前端架构约束](../../frontend/ARCHITECTURE.md)
- [测试策略](../../docs/testing/strategy/test-strategy.md)
- [架构检查脚本](../../scripts/check_architecture.py)

---

**最后更新**: 2025-11-19
**维护者**: DevOps Team
