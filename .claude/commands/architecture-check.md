# 架构合规检查

使用 Explore agent 检查代码是否符合项目架构规范。

---

请对 $ARGUMENTS 进行架构合规检查：

## 检查范围
- 如果参数为空，检查整个 `backend/app/` 目录
- 如果指定了路径，只检查该路径

## 检查项

### 1. API 层检查
- [ ] 所有端点是否只使用 POST 方法（禁止 GET/PUT/DELETE）
- [ ] URL 格式是否符合 `/api/v1/{module}/{action}`
- [ ] 是否有完整的 8 段式文档注释

### 2. Service 层检查
- [ ] 文件命名是否为 `{action}_service.py`
- [ ] 每个文件是否包含 Service + Converter + Builder 三个类
- [ ] Converter 所有方法是否使用 `@staticmethod`
- [ ] Builder 所有方法是否使用 `@staticmethod`
- [ ] Service 是否只负责权限检查和编排（无业务逻辑）

### 3. Repository 层检查
- [ ] 是否只包含纯 CRUD 操作
- [ ] 是否有业务逻辑混入（不应该有）

### 4. 层次职责检查
- [ ] Controller 是否只做接收请求和返回响应
- [ ] 业务计算是否都在 Converter 中
- [ ] 数据构建是否都在 Builder 中

## 输出格式

```
## 检查结果

### ✅ 合规项
- [列出符合规范的项目]

### ❌ 违规项
- **文件**: `path/to/file.py:line`
- **问题**: 具体描述
- **修复建议**: 如何修复
- **参考**: backend/ARCHITECTURE.md 第 X 节

### 📊 统计
- 检查文件数: X
- 合规率: X%
- P0 问题: X 个
- P1 问题: X 个

### 🔧 修复优先级
1. [最紧急的问题]
2. [次要问题]
...
```

## 参考文档
- backend/ARCHITECTURE.md
- docs/design/architecture/backend-architecture.md
