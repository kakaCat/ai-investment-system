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
- [AI 功能设置](guides/ai-setup.md) - Ollama/DeepSeek 配置 ⭐
- [数据源配置](guides/data-source-setup.md) - Tushare/AkShare 配置 ⭐ NEW
- [AI 功能测试](guides/ai-testing-guide.md) - AI 功能测试验证 ⭐
- [开发指南](guides/development/) - 开发规范
- [部署指南](guides/deployment/) - 部署流程

### [项目状态](PROJECT-STATUS.md) ⭐⭐ **必读**
项目当前进度总览

- [项目状态总览](PROJECT-STATUS.md) - 整体进度65%，下一步计划 ⭐⭐

### [AI 功能实现文档](AI-IMPLEMENTATION-SUMMARY.md) ⭐
AI 功能实现总结和验证报告

- [AI + 数据完成报告](AI-AND-DATA-INTEGRATION-COMPLETE.md) - 综合完成报告 ✅
- [AI 实现总结](AI-IMPLEMENTATION-SUMMARY.md) - 技术实现详情
- [AI 功能完成报告](AI-FEATURES-COMPLETED.md) - 完成清单
- [AI 验证报告](AI-VERIFICATION-REPORT.md) - 真实AI调用验证 ✅
- [数据源集成报告](DATA-SOURCE-INTEGRATION.md) - 真实股票数据集成 ✅

### [归档](archive/)
已废弃或历史文档

## 📖 快速开始

### 新用户
1. **[项目状态总览](PROJECT-STATUS.md)** ⭐⭐ - 了解当前进度和下一步计划
2. [产品需求](prd/v3/main.md) - 了解产品功能
3. [数据库设计](design/database/schema-v1.md) - 了解数据结构

### 开发配置
4. [MCP 设置](guides/setup/README.md) - 配置开发环境
5. [AI 功能设置](guides/ai-setup.md) - 配置 AI 功能（Ollama/DeepSeek） ⭐
6. [数据源配置](guides/data-source-setup.md) - 配置真实股票数据（Tushare/AkShare） ⭐

### 验证测试
7. [AI 功能验证](AI-VERIFICATION-REPORT.md) - 验证 AI 功能是否正常工作 ✅
8. 运行测试脚本: `python scripts/quick_ai_test.py`

## 📐 文档规范

- [全局规范](~/.claude/CLAUDE.md) - 所有项目通用
- [项目配置](../CLAUDE.md) - 本项目说明
- [文档标准](standards/) - 详细规范和历史
