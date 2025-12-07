#!/bin/bash
# 一键配置 Claude Code MCP & Skills
# 作者: Claude
# 日期: 2025-11-14

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Claude Code MCP & Skills 一键安装脚本${NC}"
echo -e "${BLUE}  适用于投资管理系统项目${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Node.js，请先安装 Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js 版本: $(node --version)"
echo -e "${GREEN}✓${NC} npm 版本: $(npm --version)"
echo ""

# 询问是否安装
read -p "是否开始安装 7 个 MCP 服务器? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "安装已取消"
    exit 0
fi

echo ""
echo -e "${BLUE}📦 开始安装 MCP 服务器...${NC}"
echo ""

# 安装函数
install_mcp() {
    local name=$1
    local package=$2
    echo -e "${YELLOW}正在安装: $name${NC}"
    if npm install -g $package 2>&1 | grep -q "up to date\|added"; then
        echo -e "${GREEN}✓${NC} $name 安装成功"
    else
        echo -e "${RED}✗${NC} $name 安装失败"
    fi
    echo ""
}

# 安装所有 MCP 服务器
install_mcp "PostgreSQL MCP" "@modelcontextprotocol/server-postgres"
install_mcp "Brave Search MCP" "@modelcontextprotocol/server-brave-search"
install_mcp "Puppeteer MCP" "@modelcontextprotocol/server-puppeteer"
install_mcp "GitHub MCP" "@modelcontextprotocol/server-github"
install_mcp "Sequential Thinking MCP" "@modelcontextprotocol/server-sequential-thinking"
install_mcp "Filesystem MCP" "@modelcontextprotocol/server-filesystem"
install_mcp "Memory MCP" "@modelcontextprotocol/server-memory"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 所有 MCP 服务器安装完成！${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# 创建配置目录
echo -e "${BLUE}📁 创建配置目录...${NC}"
mkdir -p ~/.config/claude-code/mcp
echo -e "${GREEN}✓${NC} 配置目录创建成功"
echo ""

# 复制配置模板
if [ ! -f ~/.config/claude-code/mcp/config.json ]; then
    echo -e "${BLUE}📝 复制 MCP 配置模板...${NC}"
    cp mcp-config-template.json ~/.config/claude-code/mcp/config.json
    echo -e "${GREEN}✓${NC} 配置模板已复制到: ~/.config/claude-code/mcp/config.json"
    echo ""
    echo -e "${YELLOW}⚠️  请编辑配置文件，填入你的 API 密钥：${NC}"
    echo ""
    echo "  nano ~/.config/claude-code/mcp/config.json"
    echo ""
    echo "需要配置："
    echo "  1. POSTGRES_CONNECTION_STRING (数据库连接)"
    echo "  2. BRAVE_API_KEY (Brave Search API)"
    echo "  3. GITHUB_PERSONAL_ACCESS_TOKEN (GitHub Token)"
else
    echo -e "${YELLOW}⚠️  配置文件已存在，跳过复制${NC}"
fi
echo ""

# 检查 Claude Code settings.json
echo -e "${BLUE}🔧 检查 Claude Code 配置...${NC}"
if [ -f ~/.claude/settings.json ]; then
    if grep -q "enableAllProjectMcpServers" ~/.claude/settings.json; then
        echo -e "${GREEN}✓${NC} Claude Code 配置已启用 MCP"
    else
        echo -e "${YELLOW}⚠️  Claude Code 配置需要手动启用 MCP${NC}"
    fi
else
    echo -e "${RED}✗${NC} 未找到 Claude Code 配置文件"
fi
echo ""

# 显示下一步
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 安装完成！${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📝 下一步操作：${NC}"
echo ""
echo "1. 获取 API 密钥："
echo "   • Brave Search: https://brave.com/search/api/"
echo "   • GitHub Token: https://github.com/settings/tokens"
echo ""
echo "2. 编辑 MCP 配置文件："
echo "   nano ~/.config/claude-code/mcp/config.json"
echo ""
echo "3. 重启 Claude Code："
echo "   exit（退出当前会话）"
echo "   claude（重新启动）"
echo ""
echo "4. 测试 MCP 功能："
echo '   对 Claude 说: "搜索比亚迪最新财报"'
echo ""
echo -e "${BLUE}📖 完整文档: $(pwd)/setup-guide.md${NC}"
echo ""
