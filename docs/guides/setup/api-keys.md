# API 密钥获取指南

## 🔑 Brave Search API Key（必需，用于网络搜索）

### 获取步骤：

1. **访问 Brave Search API 官网**
   ```
   https://brave.com/search/api/
   ```

2. **注册账号**
   - 点击 "Sign Up" 或 "Get Started"
   - 使用 GitHub 或 Email 注册

3. **获取 API Key**
   - 登录后进入 Dashboard
   - 点击 "API Keys" 或 "Create API Key"
   - 复制你的 API Key（格式：`BSAxxx...`）

4. **免费额度**
   - ✅ 每月免费 **2,000 次查询**
   - 适合个人投资分析使用

### 添加到配置：

```bash
nano ~/.config/claude-code/mcp/config.json
```

修改：
```json
{
  "brave-search": {
    "env": {
      "BRAVE_API_KEY": "BSA_YOUR_KEY_HERE"
    }
  }
}
```

---

## 🐙 GitHub Personal Access Token（必需，用于代码管理）

### 获取步骤：

1. **访问 GitHub Settings**
   ```
   https://github.com/settings/tokens
   ```

2. **创建新 Token**
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 输入密码确认

3. **配置权限**
   勾选以下权限：
   - ✅ `repo` - 完整的仓库访问权限
   - ✅ `workflow` - 工作流权限
   - ✅ `read:org` - 读取组织信息
   - ✅ `read:user` - 读取用户信息

4. **生成并复制**
   - 点击 "Generate token"
   - **立即复制** Token（格式：`ghp_xxx...`）
   - ⚠️ 一旦离开页面，Token 将无法再次查看

### 添加到配置：

```json
{
  "github": {
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN_HERE"
    }
  }
}
```

---

## 🐘 PostgreSQL 连接字符串（如果使用数据库）

### 本地 PostgreSQL：

```
postgresql://username:password@localhost:5432/database_name
```

### 示例：

```
postgresql://postgres:mypassword@localhost:5432/investment_db
```

### 云数据库（Supabase/Neon/Railway）：

从云服务商获取连接字符串，格式类似：
```
postgresql://user:pass@db.example.com:5432/dbname?sslmode=require
```

### 添加到配置：

```json
{
  "postgres": {
    "env": {
      "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/dbname"
    }
  }
}
```

---

## 🔐 完整配置示例

打开 `~/.config/claude-code/mcp/config.json`，填入你的密钥：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "args": [],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://postgres:mypassword@localhost:5432/investment_db"
      },
      "disabled": false
    },
    "brave-search": {
      "command": "mcp-server-brave-search",
      "args": [],
      "env": {
        "BRAVE_API_KEY": "BSA1234567890abcdef"
      },
      "disabled": false
    },
    "github": {
      "command": "mcp-server-github",
      "args": [],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_1234567890abcdefghijklmnop"
      },
      "disabled": false
    },
    "puppeteer": {
      "command": "mcp-server-puppeteer",
      "args": [],
      "env": {},
      "disabled": false
    },
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking",
      "args": [],
      "env": {},
      "disabled": false
    },
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["/Users/mac/Documents/ai/stock"],
      "env": {},
      "disabled": false
    },
    "memory": {
      "command": "mcp-server-memory",
      "args": [],
      "env": {},
      "disabled": false
    }
  }
}
```

---

## 🧪 测试配置

配置完成后，重启 Claude Code 并测试：

### 测试 Brave Search：
```
搜索"比亚迪最新财报"
```

### 测试 GitHub：
```
列出我的所有仓库
```

### 测试 PostgreSQL：
```
查询数据库中的所有表
```

---

## ❓ 常见问题

### Q: Brave API Key 无效
A: 确认 Key 格式正确（以 `BSA` 开头），检查是否超出配额

### Q: GitHub Token 权限不足
A: 重新生成 Token，确保勾选了 `repo` 和 `workflow` 权限

### Q: PostgreSQL 连接失败
A:
- 检查数据库是否运行：`pg_isready`
- 检查连接字符串格式
- 确认用户名密码正确

### Q: 如何暂时禁用某个 MCP？
A: 在配置中设置 `"disabled": true`

```json
{
  "postgres": {
    "disabled": true
  }
}
```

---

## 📝 安全提示

⚠️ **重要**：
- 不要将 API Key 提交到 Git 仓库
- 定期轮换 GitHub Token
- 使用环境变量存储敏感信息
- 限制 Token 权限范围

### 建议：使用环境变量

创建 `~/.config/claude-code/mcp/.env`:
```bash
BRAVE_API_KEY=BSA_your_key
GITHUB_TOKEN=ghp_your_token
POSTGRES_URL=postgresql://...
```

在配置中引用：
```json
{
  "env": {
    "BRAVE_API_KEY": "${BRAVE_API_KEY}"
  }
}
```

---

**💡 提示**: 所有这些 API 密钥都是可选的，可以按需配置。没有 API Key 也可以使用其他 MCP 功能。
