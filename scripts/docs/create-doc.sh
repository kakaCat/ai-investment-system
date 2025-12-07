#!/bin/bash
# 文档创建辅助脚本
# 按照标准模板创建新文档

set -e

PROJECT_ROOT="/Users/mac/Documents/ai/stock"
DOCS_DIR="$PROJECT_ROOT/docs"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 显示帮助
show_help() {
    cat << EOF
用法: $0 <类型> <路径> <文件名>

参数:
  类型    文档类型: prd, design, guide, api, test
  路径    相对路径（从 docs/ 开始）
  文件名  文件名（不含.md）

示例:
  # 创建 PRD 文档
  $0 prd prd/v4 main

  # 创建设计文档
  $0 design design/features/payment requirements

  # 创建指南文档
  $0 guide guides/deployment docker-deploy

文档类型说明:
  prd      产品需求文档
  design   设计文档（架构/数据库/功能）
  guide    指南文档（setup/development/deployment）
  api      API 文档
  test     测试文档
  adr      决策记录（Architecture Decision Record）
EOF
}

# 获取当前日期
get_date() {
    date +"%Y-%m-%d"
}

# PRD 模板
template_prd() {
    local title="$1"
    cat << EOF
# ${title}

> **版本**: v1.0
> **日期**: $(get_date)
> **状态**: 草稿

---

## 1. 概述

### 1.1 背景

[描述项目背景和目标]

### 1.2 目标

- 目标 1
- 目标 2

### 1.3 范围

#### 包含
- 功能 A
- 功能 B

#### 不包含
- [明确不包含的内容]

---

## 2. 功能需求

### 2.1 核心功能

#### 功能 A

**功能描述**:
[详细描述]

**用户故事**:
作为 [角色]，我想要 [功能]，以便 [价值]

**验收标准**:
- [ ] 标准 1
- [ ] 标准 2

---

## 3. 非功能需求

### 3.1 性能需求
- 响应时间: < 500ms
- 并发用户: 1000+

### 3.2 安全需求
- [安全要求]

---

## 4. 技术方案（概要）

### 4.1 技术栈
- 前端: React
- 后端: NestJS
- 数据库: PostgreSQL

---

## 5. 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M1 | YYYY-MM-DD | [交付物] |

---

## 附录

### 参考资料
- [相关文档]

### 术语表
| 术语 | 定义 |
|------|------|
| XXX | [定义] |
EOF
}

# 设计文档模板
template_design() {
    local title="$1"
    cat << EOF
# ${title}

> **日期**: $(get_date)
> **作者**: [作者]
> **状态**: 设计中

---

## 1. 概述

### 1.1 目标

[设计目标]

### 1.2 范围

[设计范围]

---

## 2. 需求分析

### 2.1 功能需求

- 需求 1
- 需求 2

### 2.2 非功能需求

- 性能
- 可维护性
- 可扩展性

---

## 3. 设计方案

### 3.1 整体架构

\`\`\`
[架构图或描述]
\`\`\`

### 3.2 核心组件

#### 组件 A

**职责**:
[描述]

**接口**:
\`\`\`typescript
interface ComponentA {
  method(): void;
}
\`\`\`

---

## 4. 数据模型

### 4.1 实体定义

\`\`\`typescript
interface Entity {
  id: string;
  // ...
}
\`\`\`

### 4.2 关系

[实体关系图或描述]

---

## 5. API 设计

### 5.1 接口列表

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 接口A | GET | /api/xxx | [说明] |

---

## 6. 实现细节

### 6.1 关键算法

[算法描述]

### 6.2 技术选型

| 技术 | 选择 | 原因 |
|------|------|------|
| 框架 | NestJS | [原因] |

---

## 7. 测试计划

### 7.1 单元测试

- [ ] 测试用例 1

### 7.2 集成测试

- [ ] 测试场景 1

---

## 8. 部署方案

[部署架构和流程]

---

## 9. 风险与挑战

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 风险1 | 高 | [措施] |

---

## 10. 参考资料

- [相关文档]
EOF
}

# 指南文档模板
template_guide() {
    local title="$1"
    cat << EOF
# ${title}

> **更新日期**: $(get_date)

---

## 📋 概述

[简要说明本指南的目的和适用场景]

---

## 🎯 前置条件

在开始之前，请确保：

- [ ] 已安装 Node.js (v18+)
- [ ] 已安装 Git
- [ ] [其他要求]

---

## 🚀 快速开始

### Step 1: [步骤标题]

\`\`\`bash
# 命令示例
npm install
\`\`\`

**说明**: [详细说明]

### Step 2: [步骤标题]

\`\`\`bash
# 命令示例
npm run dev
\`\`\`

---

## 📖 详细说明

### [主题 A]

#### [子主题 1]

[详细内容]

\`\`\`bash
# 示例代码
\`\`\`

#### [子主题 2]

[详细内容]

---

## 🔧 配置说明

### 配置文件

文件位置: \`config/xxx.json\`

\`\`\`json
{
  "key": "value"
}
\`\`\`

**配置项说明**:

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| key | string | [说明] | value |

---

## ⚠️ 常见问题

### Q: [问题描述]

**A**: [解决方案]

\`\`\`bash
# 解决命令
\`\`\`

---

## 📚 参考资料

- [官方文档](https://example.com)
- [相关指南](../other-guide.md)

---

## 🔄 更新日志

| 日期 | 变更内容 |
|------|----------|
| $(get_date) | 初始版本 |
EOF
}

# ADR 模板
template_adr() {
    local title="$1"
    local number="$2"
    cat << EOF
# ADR-${number}: ${title}

**日期**: $(get_date)
**状态**: 已提议 | 已接受 | 已废弃 | 已替代

---

## 背景

[描述需要做决策的背景和问题]

---

## 决策

我们决定 [决策内容]

---

## 理由

### 选项分析

#### 选项 A: [方案名称]

**优点**:
- 优点 1
- 优点 2

**缺点**:
- 缺点 1
- 缺点 2

#### 选项 B: [方案名称]

**优点**:
- 优点 1

**缺点**:
- 缺点 1

### 最终选择

我们选择了 **选项 A**，因为：
1. 理由 1
2. 理由 2

---

## 结果

**积极影响**:
- 影响 1
- 影响 2

**消极影响**:
- 影响 1

**权衡**:
- 权衡点 1

---

## 参考资料

- [相关文档]
- [技术文章]
EOF
}

# 创建文档
create_document() {
    local doc_type="$1"
    local rel_path="$2"
    local filename="$3"

    local full_dir="$DOCS_DIR/$rel_path"
    local full_path="$full_dir/${filename}.md"

    # 提取标题
    local title=$(echo "$filename" | sed 's/-/ /g' | sed 's/\b\w/\u&/g')

    # 创建目录
    mkdir -p "$full_dir"

    # 根据类型生成模板
    case "$doc_type" in
        prd)
            template_prd "$title" > "$full_path"
            ;;
        design)
            template_design "$title" > "$full_path"
            ;;
        guide)
            template_guide "$title" > "$full_path"
            ;;
        adr)
            # 提取编号
            local number=$(echo "$filename" | grep -oP '^\d+' || echo "001")
            template_adr "$title" "$number" > "$full_path"
            ;;
        *)
            echo -e "${RED}错误: 不支持的文档类型: $doc_type${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac

    echo -e "${GREEN}✓${NC} 文档已创建: $full_path"
    echo ""
    echo -e "${BLUE}下一步:${NC}"
    echo "1. 编辑文档: code $full_path"
    echo "2. 预览文档: cat $full_path"
    echo ""
}

# 主流程
main() {
    if [ "$#" -lt 1 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        show_help
        exit 0
    fi

    if [ "$#" -lt 3 ]; then
        echo -e "${RED}错误: 参数不足${NC}"
        echo ""
        show_help
        exit 1
    fi

    local doc_type="$1"
    local rel_path="$2"
    local filename="$3"

    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  文档创建工具${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo ""

    create_document "$doc_type" "$rel_path" "$filename"
}

main "$@"
