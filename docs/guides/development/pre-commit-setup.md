# Pre-commit Hooks设置指南

> 本地代码提交前自动检查

---

## 📐 概述

Pre-commit hooks在代码提交到Git前自动运行检查，确保代码质量和架构符合性。

**优势**:
- ✅ 早期发现问题
- ✅ 自动化代码格式化
- ✅ 强制架构约束
- ✅ 防止提交敏感信息
- ✅ 统一团队代码风格

---

## 🔧 安装配置

### 第1步: 安装pre-commit

```bash
# 安装pre-commit工具
pip install pre-commit

# 验证安装
pre-commit --version
```

### 第2步: 安装Git hooks

```bash
# 在项目根目录执行
pre-commit install

# 输出: pre-commit installed at .git/hooks/pre-commit
```

### 第3步: 首次运行（可选）

```bash
# 在所有文件上运行一次
pre-commit run --all-files
```

---

## 📋 检查项说明

### 1. 通用检查

| 检查 | 说明 | 自动修复 |
|------|------|---------|
| `trailing-whitespace` | 删除行尾空格 | ✅ |
| `end-of-file-fixer` | 确保文件以换行符结尾 | ✅ |
| `check-yaml` | 检查YAML语法 | ❌ |
| `check-json` | 检查JSON语法 | ❌ |
| `check-added-large-files` | 检查大文件（>1MB） | ❌ |
| `check-merge-conflict` | 检查合并冲突标记 | ❌ |
| `mixed-line-ending` | 统一行结束符为LF | ✅ |

### 2. Python检查（后端）

| 检查 | 说明 | 自动修复 |
|------|------|---------|
| `black` | 代码格式化 | ✅ |
| `flake8` | 代码风格检查 | ❌ |
| `isort` | 导入语句排序 | ✅ |
| `mypy` | 类型检查 | ❌ |
| `bandit` | 安全漏洞扫描 | ❌ |

### 3. TypeScript检查（前端）

| 检查 | 说明 | 自动修复 |
|------|------|---------|
| `eslint` | 代码风格和错误检查 | 部分 |

### 4. 架构检查（自定义）

| 检查 | 说明 | 自动修复 |
|------|------|---------|
| `architecture-check` | 架构符合性检查 | ❌ |

检查内容:
- ✅ 所有API使用POST方法
- ✅ Service文件命名规范
- ✅ Converter/Builder使用@staticmethod
- ✅ Repository无业务逻辑

### 5. 安全检查

| 检查 | 说明 | 自动修复 |
|------|------|---------|
| `detect-secrets` | 检测API密钥、密码等敏感信息 | ❌ |

---

## 🚀 使用方式

### 自动运行（推荐）

```bash
# 正常提交代码，hooks自动运行
git add .
git commit -m "feat: Add new feature"

# 如果检查失败，修复问题后重新提交
git add .
git commit -m "feat: Add new feature"
```

### 手动运行

```bash
# 运行所有检查
pre-commit run --all-files

# 运行特定检查
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run architecture-check

# 只检查staged的文件
pre-commit run
```

### 跳过检查（不推荐）

```bash
# 紧急情况下跳过pre-commit检查
git commit --no-verify -m "fix: Emergency hotfix"
```

**警告**: 跳过检查可能导致CI失败，仅在紧急情况使用！

---

## 📊 检查流程

```
git commit
    ↓
1. 通用检查（YAML、JSON、大文件等）
    ↓
2. Python检查（black → isort → flake8 → mypy）
    ↓
3. TypeScript检查（eslint）
    ↓
4. 架构检查（scripts/check_architecture.py）
    ↓
5. 安全检查（bandit、detect-secrets）
    ↓
✅ 全部通过 → 提交成功
❌ 有失败 → 提交中断，显示错误信息
```

---

## 🔧 配置文件

### .pre-commit-config.yaml

项目的pre-commit配置文件位于根目录: `.pre-commit-config.yaml`

### 自定义配置

如需修改检查规则：

```yaml
# .pre-commit-config.yaml

# 禁用某个检查
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        exclude: ^path/to/exclude/  # 排除某些文件

# 修改参数
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--ignore=E501']
```

---

## ❗ 常见问题

### Q1: Black和Flake8冲突

**问题**: Black格式化后Flake8报错

**解决**:
```yaml
# 在.pre-commit-config.yaml中配置
- id: flake8
  args: ['--max-line-length=120', '--extend-ignore=E203,W503']
```

### Q2: 检查运行很慢

**问题**: 每次提交都要等很久

**解决**:
```bash
# 只检查staged的文件（不加--all-files）
pre-commit run

# 禁用某些慢的检查（如mypy）
# 在.pre-commit-config.yaml中注释掉
```

### Q3: 架构检查失败

**问题**: `architecture-check` 报错

**解决**:
```bash
# 查看详细错误
python scripts/check_architecture.py

# 根据错误提示修复代码
# 例如: Converter方法缺少@staticmethod
```

### Q4: 无法检测到Python

**问题**: `python: command not found`

**解决**:
```bash
# 指定Python版本
pre-commit run --hook-stage manual

# 或在配置中指定
default_language_version:
  python: python3.11
```

### Q5: 需要更新hooks

**问题**: hooks版本过旧

**解决**:
```bash
# 更新所有hooks到最新版本
pre-commit autoupdate

# 清理缓存
pre-commit clean

# 重新安装
pre-commit install
```

---

## 📈 最佳实践

### 1. 定期更新

```bash
# 每月更新一次hooks版本
pre-commit autoupdate
```

### 2. 团队统一配置

- 所有团队成员使用相同的`.pre-commit-config.yaml`
- 配置文件纳入版本控制
- CI/CD运行相同的检查

### 3. 渐进式启用

```yaml
# 对于大型项目，先从简单检查开始
fail_fast: true  # 第一个错误就停止

# 逐步启用更严格的检查
- id: mypy
  exclude: ^old_code/  # 先排除旧代码
```

### 4. 自动修复优先

```bash
# 使用自动修复的工具
# black、isort等会自动修复格式问题
# 提交前运行一次:
pre-commit run --all-files
```

---

## 🔗 相关资源

### 内部文档
- [架构检查脚本](../../../scripts/check_architecture.py)
- [后端架构约束](../../../backend/ARCHITECTURE.md)
- [CI/CD配置](../../../.github/workflows/README.md)

### 外部资源
- [Pre-commit官方文档](https://pre-commit.com/)
- [Black文档](https://black.readthedocs.io/)
- [Flake8文档](https://flake8.pycqa.org/)
- [ESLint文档](https://eslint.org/)

---

## 📝 检查清单

设置pre-commit后确认：

- [ ] 已安装pre-commit: `pre-commit --version`
- [ ] 已安装Git hooks: `pre-commit install`
- [ ] 配置文件存在: `.pre-commit-config.yaml`
- [ ] 运行一次全面检查: `pre-commit run --all-files`
- [ ] 测试提交流程: 修改文件并commit
- [ ] 团队成员都已安装

---

**最后更新**: 2025-11-19
**维护者**: DevOps Team
