# Claude Code MCP & Skills 配置指南

## 📦 已推荐安装的 MCP 服务器

### 1. **PostgreSQL MCP** ⭐⭐⭐⭐⭐
**用途**: 直接查询和操作投资管理数据库
- 查询持仓数据
- 分析历史交易
- 生成数据报表

### 2. **Brave Search MCP** ⭐⭐⭐⭐⭐
**用途**: 实时搜索财经新闻、股票信息
- 搜索最新财报
- 查找公司新闻
- 获取行业动态

### 3. **Puppeteer MCP** ⭐⭐⭐⭐
**用途**: Web自动化抓取股票数据
- 抓取股票行情
- 获取财务数据
- 自动化测试前端

### 4. **GitHub MCP** ⭐⭐⭐⭐
**用途**: 管理代码仓库
- 创建/管理 Pull Requests
- 查看 Issues
- 触发 CI/CD

### 5. **Sequential Thinking MCP** ⭐⭐⭐⭐⭐
**用途**: 复杂投资分析
- 多步骤财务分析
- 投资策略推理
- 风险评估

### 6. **Filesystem MCP** ⭐⭐⭐⭐
**用途**: 项目文件管理
- 读写配置文件
- 管理文档
- 处理导入导出

### 7. **Memory MCP** ⭐⭐⭐⭐
**用途**: AI记忆你的偏好
- 记住投资偏好
- 保存分析结果
- 持久化配置

---

## 🚀 快速开始

### Step 1: 安装所有 MCP 服务器

```bash
cd /Users/mac/Documents/ai/stock
chmod +x setup-mcp-skills.sh
./setup-mcp-skills.sh
```

### Step 2: 获取必要的 API 密钥

#### Brave Search API Key (免费)
1. 访问: https://brave.com/search/api/
2. 注册账号
3. 获取 API Key（每月免费 2000 次查询）

#### GitHub Personal Access Token
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限: `repo`, `workflow`, `read:org`
4. 生成并复制 token

### Step 3: 配置 MCP 服务器

```bash
# 创建配置目录
mkdir -p ~/.config/claude-code/mcp

# 复制模板并编辑
cp mcp-config-template.json ~/.config/claude-code/mcp/config.json

# 编辑配置文件，填入你的 API 密钥
nano ~/.config/claude-code/mcp/config.json
```

**需要修改的内容：**
```json
{
  "POSTGRES_CONNECTION_STRING": "postgresql://your_user:your_password@localhost:5432/your_db",
  "BRAVE_API_KEY": "BSA_YOUR_KEY_HERE",
  "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN_HERE"
}
```

### Step 4: 启用推荐的 Skills

编辑 `~/.claude/settings.json`，添加以下配置：

```json
{
  "enabledPlugins": {
    "document-skills@anthropic-agent-skills": true,
    "example-skills@anthropic-agent-skills": true,
    "cc_chrome_devtools_mcp_skill@cc_chrome_devtools_mcp_skill-plugin-marketplace": true
  },
  "enableAllProjectMcpServers": true
}
```

### Step 5: 重启 Claude Code

```bash
# 退出当前 Claude Code 会话
exit

# 重新启动
claude
```

---

## 🔧 验证安装

启动 Claude Code 后，尝试以下命令验证：

```
# 测试 PostgreSQL 连接
请查询数据库中的所有表

# 测试 Brave Search
搜索"比亚迪最新财报"

# 测试 GitHub
列出我的仓库

# 测试 Sequential Thinking
分析一下腾讯控股的投资价值，考虑财务、行业、估值等多个维度
```

---

## 📊 推荐的投资分析工作流

### 工作流 1: 股票深度分析
```
1. 使用 Brave Search 搜索公司最新新闻
2. 使用 Puppeteer 抓取股价和财务数据
3. 使用 PostgreSQL 查询历史持仓记录
4. 使用 Sequential Thinking 进行综合分析
5. 使用 Memory 保存分析结果
```

### 工作流 2: 持仓组合优化
```
1. 从 PostgreSQL 获取当前持仓
2. 使用 Brave Search 搜索相关事件
3. 使用 Sequential Thinking 分析影响
4. 生成调仓建议
5. 保存到 Filesystem
```

### 工作流 3: 自动化数据采集
```
1. 使用 Puppeteer 定时抓取股票数据
2. 存入 PostgreSQL 数据库
3. 使用 GitHub 提交代码变更
4. 触发 CI/CD 部署
```

---

## 🎯 高级配置

### 为特定项目配置 MCP

在项目根目录创建 `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "stock-data-api": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "env": {
        "ALLOWED_DOMAINS": "finance.yahoo.com,api.nasdaq.com"
      }
    }
  }
}
```

### 自定义 Skill

创建 `.claude/skills/investment-analysis.md`:

```markdown
---
name: investment-analysis
description: 执行完整的股票投资分析
triggers:
  - "分析.*股票"
  - "投资建议"
tools:
  - Bash
  - Read
  - Write
---

# 投资分析流程

1. 搜索公司最新新闻（使用 Brave Search）
2. 查询数据库获取历史数据
3. 计算估值指标
4. 生成分析报告
```

---

## 🐛 常见问题

### Q: MCP 服务器启动失败
A: 检查 `~/.config/claude-code/mcp/config.json` 中的路径和 API 密钥是否正确

### Q: PostgreSQL 连接失败
A: 确保数据库正在运行，连接字符串格式正确

### Q: Brave Search 返回空结果
A: 检查 API Key 是否有效，是否超出配额

### Q: 如何查看 MCP 日志
A: 日志位置: `~/.claude/debug/mcp-*.log`

---

## 📚 更多资源

- [Claude Code MCP 官方文档](https://docs.claude.com/en/docs/claude-code/mcp)
- [MCP Servers 列表](https://www.claudemcp.com/servers)
- [Skills 开发指南](https://github.com/anthropics/skills)
- [MCP 规范](https://modelcontextprotocol.io/)

---

**💡 提示**: 不要一次性启用所有 MCP 服务器，按需启用可以提高性能。
