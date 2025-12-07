#!/bin/bash
# 文档自动整理脚本
# 按照金字塔原理组织文档结构

set -e

PROJECT_ROOT="/Users/mac/Documents/ai/stock"
DOCS_DIR="$PROJECT_ROOT/docs"
BACKUP_DIR="$PROJECT_ROOT/backup/docs-$(date +%Y%m%d-%H%M%S)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 模式：dry-run 或 execute
MODE="${1:---dry-run}"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  文档自动整理脚本${NC}"
echo -e "${BLUE}  基于金字塔原理组织文档结构${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

if [ "$MODE" == "--dry-run" ]; then
    echo -e "${YELLOW}🔍 模式: 预览模式（不会实际移动文件）${NC}"
    echo -e "${YELLOW}   使用 --execute 参数执行实际操作${NC}"
else
    echo -e "${GREEN}✅ 模式: 执行模式（将实际移动文件）${NC}"
    echo -e "${YELLOW}   备份目录: $BACKUP_DIR${NC}"
fi
echo ""

# 创建备份
backup_docs() {
    if [ "$MODE" == "--execute" ]; then
        echo -e "${BLUE}📦 创建备份...${NC}"
        mkdir -p "$BACKUP_DIR"
        cp -r "$DOCS_DIR" "$BACKUP_DIR/"
        echo -e "${GREEN}✓${NC} 备份完成: $BACKUP_DIR"
        echo ""
    fi
}

# 创建目录结构
create_structure() {
    echo -e "${BLUE}📁 创建标准目录结构...${NC}"

    local dirs=(
        "$DOCS_DIR/prd/v3/sections"
        "$DOCS_DIR/prd/v3/archive"
        "$DOCS_DIR/prd/v3/attachments/diagrams"
        "$DOCS_DIR/design/architecture"
        "$DOCS_DIR/design/database"
        "$DOCS_DIR/design/api"
        "$DOCS_DIR/design/features/events"
        "$DOCS_DIR/design/features/ai"
        "$DOCS_DIR/guides/setup"
        "$DOCS_DIR/guides/development"
        "$DOCS_DIR/guides/deployment"
        "$DOCS_DIR/archive"
        "$PROJECT_ROOT/scripts/docs"
        "$PROJECT_ROOT/config"
    )

    for dir in "${dirs[@]}"; do
        if [ "$MODE" == "--execute" ]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✓${NC} 创建: $dir"
        else
            echo -e "${BLUE}→${NC} 将创建: $dir"
        fi
    done
    echo ""
}

# 移动文件函数
move_file() {
    local src="$1"
    local dest="$2"
    local desc="$3"

    if [ -f "$src" ]; then
        if [ "$MODE" == "--execute" ]; then
            mkdir -p "$(dirname "$dest")"
            mv "$src" "$dest"
            echo -e "${GREEN}✓${NC} 移动: $desc"
            echo -e "   ${src##*/} → ${dest#$PROJECT_ROOT/}"
        else
            echo -e "${BLUE}→${NC} 将移动: $desc"
            echo -e "   $src → $dest"
        fi
    else
        echo -e "${YELLOW}⚠${NC}  文件不存在: $src"
    fi
}

# 整理 PRD 文档
organize_prd() {
    echo -e "${BLUE}📄 整理 PRD 文档...${NC}"

    # 主 PRD 文档
    move_file \
        "$DOCS_DIR/prd-v3-investment-management.md" \
        "$DOCS_DIR/prd/v3/main.md" \
        "PRD v3 主文档"

    # 备份文件
    move_file \
        "$DOCS_DIR/prd-v3-investment-management.md.backup" \
        "$DOCS_DIR/prd/v3/archive/main-v3.0.md" \
        "PRD v3.0 备份"

    # 章节文件（2.9 事件分析）
    move_file \
        "$DOCS_DIR/prd-section-2.9-events.md" \
        "$DOCS_DIR/prd/v3/sections/02.9-events.md" \
        "PRD 第2.9章 事件分析"

    # 旧版本 PRD
    if [ -f "$DOCS_DIR/prd-investment-ai.md" ]; then
        move_file \
            "$DOCS_DIR/prd-investment-ai.md" \
            "$DOCS_DIR/archive/prd-ai-old.md" \
            "旧版 AI PRD（已废弃）"
    fi

    echo ""
}

# 整理设计文档
organize_design() {
    echo -e "${BLUE}🎨 整理设计文档...${NC}"

    # 数据库设计
    move_file \
        "$DOCS_DIR/db-schema-v1.md" \
        "$DOCS_DIR/design/database/schema-v1.md" \
        "数据库 Schema v1"

    # 事件分析功能设计
    move_file \
        "$DOCS_DIR/event-analysis-enhancement.md" \
        "$DOCS_DIR/design/features/events/requirements.md" \
        "事件分析需求"

    move_file \
        "$DOCS_DIR/event-adapter-implementation.md" \
        "$DOCS_DIR/design/features/events/implementation.md" \
        "事件适配器实现"

    move_file \
        "$DOCS_DIR/ai-event-integration.md" \
        "$DOCS_DIR/design/features/events/ai-integration.md" \
        "AI 事件集成"

    # 多用户多账户设计
    move_file \
        "$DOCS_DIR/multi-user-multi-account.md" \
        "$DOCS_DIR/design/features/multi-user-design.md" \
        "多用户多账户设计"

    # 单页股票中心
    move_file \
        "$DOCS_DIR/one-page-stock-center.md" \
        "$DOCS_DIR/design/features/stock-center-design.md" \
        "单页股票中心设计"

    echo ""
}

# 整理指南文档
organize_guides() {
    echo -e "${BLUE}📚 整理指南文档...${NC}"

    # MCP 设置指南
    move_file \
        "$PROJECT_ROOT/setup-guide.md" \
        "$DOCS_DIR/guides/setup/mcp-setup.md" \
        "MCP 设置指南"

    move_file \
        "$PROJECT_ROOT/api-keys-guide.md" \
        "$DOCS_DIR/guides/setup/api-keys.md" \
        "API 密钥指南"

    move_file \
        "$PROJECT_ROOT/MCP-SETUP-README.md" \
        "$DOCS_DIR/guides/setup/README.md" \
        "MCP 设置总览"

    echo ""
}

# 整理脚本和配置
organize_scripts_config() {
    echo -e "${BLUE}🔧 整理脚本和配置文件...${NC}"

    # 脚本文件
    for script in setup-mcp-skills.sh quick-setup.sh; do
        if [ -f "$PROJECT_ROOT/$script" ]; then
            move_file \
                "$PROJECT_ROOT/$script" \
                "$PROJECT_ROOT/scripts/setup/$script" \
                "安装脚本: $script"
        fi
    done

    # 配置文件
    move_file \
        "$PROJECT_ROOT/mcp-config-template.json" \
        "$PROJECT_ROOT/config/mcp-config-template.json" \
        "MCP 配置模板"

    echo ""
}

# 整理临时和归档文件
organize_archive() {
    echo -e "${BLUE}🗄️  整理临时和归档文件...${NC}"

    # 合并总结
    move_file \
        "$DOCS_DIR/MERGE_SUMMARY.md" \
        "$DOCS_DIR/archive/merge-summary-20250114.md" \
        "合并总结（临时文件）"

    # 事件分析总结
    move_file \
        "$DOCS_DIR/event-analysis-summary.md" \
        "$DOCS_DIR/archive/event-analysis-summary.md" \
        "事件分析总结"

    # 简易查看器（工具文件）
    move_file \
        "$DOCS_DIR/simple-viewer.html" \
        "$DOCS_DIR/tools/simple-viewer.html" \
        "简易 Markdown 查看器"

    # 图片目录
    if [ -d "$DOCS_DIR/img" ]; then
        if [ "$MODE" == "--execute" ]; then
            mv "$DOCS_DIR/img" "$DOCS_DIR/prd/v3/attachments/diagrams"
            echo -e "${GREEN}✓${NC} 移动图片目录"
        else
            echo -e "${BLUE}→${NC} 将移动图片目录"
        fi
    fi

    # 归档目录
    if [ -d "$DOCS_DIR/archive" ] && [ -n "$(ls -A "$DOCS_DIR/archive" 2>/dev/null)" ]; then
        echo -e "${GREEN}✓${NC} 归档目录已存在"
    fi

    echo ""
}

# 创建 README 文件
create_readmes() {
    echo -e "${BLUE}📝 创建 README 索引文件...${NC}"

    if [ "$MODE" == "--execute" ]; then
        # docs/README.md
        cat > "$DOCS_DIR/README.md" << 'EOF'
# 文档导航

> 基于金字塔原理组织的项目文档

## 📚 文档结构

### [PRD](prd/)
产品需求文档，按版本组织

- [v3 当前版本](prd/v3/) - 投资管理系统 v3

### [设计文档](design/)
技术设计文档

- [架构设计](design/architecture/) - 系统架构
- [数据库设计](design/database/) - 数据库 Schema
- [功能设计](design/features/) - 具体功能设计
  - [事件分析](design/features/events/) - 事件分析与追踪

### [指南文档](guides/)
安装、开发、部署指南

- [设置指南](guides/setup/) - 环境配置、MCP 设置
- [开发指南](guides/development/) - 开发规范
- [部署指南](guides/deployment/) - 部署流程

### [归档](archive/)
已废弃或历史文档

## 📖 快速开始

1. [产品需求](prd/v3/main.md) - 了解产品功能
2. [MCP 设置](guides/setup/README.md) - 配置开发环境
3. [数据库设计](design/database/schema-v1.md) - 了解数据结构

## 📐 文档规范

参见 [文档管理规范](../DOCUMENT-MANAGEMENT-STANDARD.md)
EOF
        echo -e "${GREEN}✓${NC} 创建 docs/README.md"

        # prd/v3/README.md
        cat > "$DOCS_DIR/prd/v3/README.md" << 'EOF'
# PRD v3 - 投资管理系统

## 概述

本目录包含投资管理系统 v3 版本的产品需求文档。

## 文档结构

- `main.md` - 完整 PRD（3200+ 行）
- `sections/` - 按章节拆分的文档
- `archive/` - 历史版本备份
- `attachments/` - 附件和图表

## 主要内容

### 核心功能
1. 账户与持仓管理
2. 股票数据管理
3. AI 投资分析
4. **事件分析与追踪**（v3.1 新增）

### 文档索引

- [完整 PRD](main.md)
- [第 2.9 章：事件分析与追踪](sections/02.9-events.md)

## 版本历史

| 版本 | 日期 | 主要变更 |
|-----|------|----------|
| v3.1 | 2025-01-14 | 新增事件分析与追踪功能 |
| v3.0 | 2025-01-13 | 初始版本 |

## 相关文档

- [事件分析设计](../../design/features/events/)
- [数据库 Schema](../../design/database/schema-v1.md)
EOF
        echo -e "${GREEN}✓${NC} 创建 prd/v3/README.md"

        # design/features/events/README.md
        mkdir -p "$DOCS_DIR/design/features/events"
        cat > "$DOCS_DIR/design/features/events/README.md" << 'EOF'
# 事件分析与追踪 - 设计文档

## 概述

事件分析与追踪功能的完整设计文档，包括需求、实现和集成方案。

## 文档索引

- [需求文档](requirements.md) - 功能需求和事件类型体系
- [实现设计](implementation.md) - EventAdapter 和技术实现
- [AI 集成](ai-integration.md) - AI 分析集成方案

## 功能亮点

- 4 大类事件，16 种子类型
- AI 驱动的影响分析
- 与持仓分析深度集成
- 自动监控和智能提醒

## 相关文档

- [PRD 2.9 章节](../../../prd/v3/sections/02.9-events.md)
- [数据库 Schema](../../database/schema-v1.md)
EOF
        echo -e "${GREEN}✓${NC} 创建 design/features/events/README.md"

    else
        echo -e "${BLUE}→${NC} 将创建 README 索引文件"
    fi

    echo ""
}

# 生成整理报告
generate_report() {
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 文档整理完成！${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo ""

    if [ "$MODE" == "--dry-run" ]; then
        echo -e "${YELLOW}这是预览模式，没有实际移动文件${NC}"
        echo -e "${YELLOW}使用以下命令执行实际操作：${NC}"
        echo ""
        echo -e "  ${GREEN}$0 --execute${NC}"
        echo ""
    else
        echo -e "${GREEN}文档已按照金字塔原理重新组织${NC}"
        echo ""
        echo "📁 新的文档结构："
        echo ""
        echo "docs/"
        echo "├── README.md                     # 文档导航"
        echo "├── prd/                          # 产品需求"
        echo "│   └── v3/"
        echo "│       ├── README.md"
        echo "│       ├── main.md"
        echo "│       └── sections/"
        echo "├── design/                       # 设计文档"
        echo "│   ├── database/"
        echo "│   └── features/"
        echo "│       └── events/"
        echo "├── guides/                       # 指南文档"
        echo "│   └── setup/"
        echo "└── archive/                      # 归档"
        echo ""
        echo "📝 下一步："
        echo "1. 查看文档: cat docs/README.md"
        echo "2. 验证结构: tree docs/"
        echo "3. 检查链接: ./scripts/docs/validate-docs.sh"
        echo ""
        echo "💾 备份位置: $BACKUP_DIR"
    fi
}

# 主流程
main() {
    backup_docs
    create_structure
    organize_prd
    organize_design
    organize_guides
    organize_scripts_config
    organize_archive
    create_readmes
    generate_report
}

main
