#!/bin/bash
# Claude Code MCP & Skills 安装脚本
# 适用于投资管理系统项目

set -e

echo "🚀 开始安装 Claude Code MCP 服务器和 Skills..."
echo ""

# 创建 MCP 配置目录
mkdir -p ~/.config/claude-code/mcp

# ======================
# 1. 安装 PostgreSQL MCP
# ======================
echo "📦 安装 PostgreSQL MCP Server..."
npm install -g @modelcontextprotocol/server-postgres

# ======================
# 2. 安装 Brave Search MCP
# ======================
echo "📦 安装 Brave Search MCP Server..."
npm install -g @modelcontextprotocol/server-brave-search

# ======================
# 3. 安装 Puppeteer MCP
# ======================
echo "📦 安装 Puppeteer MCP Server..."
npm install -g @modelcontextprotocol/server-puppeteer

# ======================
# 4. 安装 GitHub MCP
# ======================
echo "📦 安装 GitHub MCP Server..."
npm install -g @modelcontextprotocol/server-github

# ======================
# 5. 安装 Sequential Thinking MCP
# ======================
echo "📦 安装 Sequential Thinking MCP Server..."
npm install -g @modelcontextprotocol/server-sequential-thinking

# ======================
# 6. 安装 Filesystem MCP
# ======================
echo "📦 安装 Filesystem MCP Server..."
npm install -g @modelcontextprotocol/server-filesystem

# ======================
# 7. 安装 Memory MCP (用于AI记忆)
# ======================
echo "📦 安装 Memory MCP Server..."
npm install -g @modelcontextprotocol/server-memory

echo ""
echo "✅ 所有 MCP 服务器安装完成！"
echo ""
echo "📝 下一步："
echo "1. 配置 MCP 服务器（需要API密钥）"
echo "2. 启用 Claude Code Skills"
echo "3. 重启 Claude Code"
echo ""
echo "配置文件位置: ~/.config/claude-code/mcp/config.json"
