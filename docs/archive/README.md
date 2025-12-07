# 归档文档

> 已废弃或历史版本的文档归档

---

## 📂 目录结构

```
archive/
├── README.md               # 本文件
├── implementation/         # 实现状态文档（历史记录）
├── prd/                    # 旧版本PRD
└── backup/                 # 文档备份
```

---

## 📋 归档内容

### implementation/

**实现状态文档** - 项目开发过程中的状态记录：
- `INTEGRATION_STATUS.md` - 前后端联调状态（已完成）
- `API_IMPLEMENTATION_STATUS.md` - API实现状态（已完成）
- `FINAL_API_STATUS.md` - 最终API状态（已完成）
- `IMPLEMENTATION_COMPLETE.md` - 实现完成记录（已完成）
- `IMPLEMENTATION_STATUS.md` - 后端实现状态（已完成）
- `implementation-check.md` - 实现检查清单（已完成）

**归档原因**: 这些文档记录了项目早期的开发进度，现在功能已完成，保留作为历史参考。

---

### prd/

**旧版本PRD**:
- `prd-v2.md` - 产品需求文档 v2.0（已被v3.1替代）

**归档原因**: 已被 docs/prd/v3/ 中的v3.1版本替代。

**当前版本**: [docs/prd/v3/main.md](../prd/v3/main.md)

---

### backup/

**文档备份**:
- `docs-20251114-023334/` - 2025-11-14的文档结构重组前备份

**归档原因**: 文档结构重组前的备份，用于恢复参考。

---

## 📝 归档规则

### 何时归档

文档应该归档当：
1. **被新版本替代** - 如PRD v2被v3替代
2. **项目阶段完成** - 如实现状态文档在项目完成后
3. **文档不再维护** - 但有历史参考价值
4. **结构重组** - 重大文档结构调整前的备份

### 归档格式

\`\`\`
archive/
└── {category}/
    └── {document-name}.md
\`\`\`

或带日期的归档：

\`\`\`
archive/
└── {category}/
    └── YYYY-MM-DD-{document-name}.md
\`\`\`

---

**归档日期**: 2025-11-19
**维护者**: Project Manager
**清理策略**: 保留2年后评估是否永久删除
