# 重构建议

分析代码异味，提供重构方案和优先级。

---

请对 $ARGUMENTS 进行重构分析：

## 检查范围
- 如果参数为空，分析整个代码库
- 如果指定路径，分析该路径

## 分析维度

### 1. 代码异味 (Code Smells)

#### 结构性问题
- 过长函数（>50行）
- 过大类（>500行）
- 参数过多（>5个）
- 嵌套过深（>3层）

#### 重复代码
- 完全重复的代码块
- 相似逻辑可抽象
- 复制粘贴痕迹

#### 命名问题
- 含义不清的变量名
- 不一致的命名风格
- 缩写过度

### 2. 设计问题

- 违反单一职责
- 紧耦合
- 缺少抽象
- 硬编码

### 3. 架构偏离

- 层次职责混乱
- 循环依赖
- 不符合项目规范

## 输出格式

```
## 重构建议报告

### 📊 分析概述
- **分析范围**: {路径}
- **代码行数**: X 行
- **技术债务评分**: X/10

---

### 🔴 高优先级重构

#### 1. 过长函数拆分

**位置**: `backend/app/services/analysis/ai_service.py:50-180`
**问题**: 函数 `analyze_portfolio` 有 130 行
**影响**: 难以理解、测试、维护

**当前结构**:
```python
async def analyze_portfolio(self, portfolio_id, user_id):
    # 1. 获取数据 (20行)
    # 2. 数据预处理 (30行)
    # 3. 构建 prompt (40行)
    # 4. 调用 AI (20行)
    # 5. 解析结果 (20行)
```

**重构方案**:
```python
async def analyze_portfolio(self, portfolio_id, user_id):
    data = await self._fetch_portfolio_data(portfolio_id, user_id)
    processed = self._preprocess_data(data)
    prompt = self._build_analysis_prompt(processed)
    response = await self._call_ai_api(prompt)
    return self._parse_ai_response(response)

async def _fetch_portfolio_data(self, portfolio_id, user_id):
    """获取投资组合数据"""
    pass

def _preprocess_data(self, data):
    """数据预处理"""
    pass

def _build_analysis_prompt(self, data):
    """构建 AI 分析 prompt"""
    pass

async def _call_ai_api(self, prompt):
    """调用 AI API"""
    pass

def _parse_ai_response(self, response):
    """解析 AI 响应"""
    pass
```

**收益**:
- 可单独测试每个步骤
- 便于复用
- 易于理解

---

#### 2. 重复代码提取

**位置**:
- `backend/app/services/account/list_service.py:30-45`
- `backend/app/services/portfolio/list_service.py:25-40`

**重复代码**:
```python
# 两个文件中几乎相同的权限检查逻辑
if not entity:
    raise NotFoundError(f"{name} not found")
if entity.user_id != user_id:
    raise PermissionError(f"No access to {name}")
if entity.is_deleted:
    raise NotFoundError(f"{name} has been deleted")
```

**重构方案**:
```python
# backend/app/core/permissions.py
def check_resource_access(entity, user_id: int, resource_name: str):
    """通用资源访问检查"""
    if not entity:
        raise NotFoundError(f"{resource_name} not found")
    if entity.user_id != user_id:
        raise PermissionError(f"No access to {resource_name}")
    if getattr(entity, 'is_deleted', False):
        raise NotFoundError(f"{resource_name} has been deleted")
    return entity

# 使用
account = check_resource_access(account, user_id, "Account")
```

---

### 🟡 中优先级重构

#### 3. 参数对象引入

**位置**: `backend/app/services/event/create_service.py:20`

**问题**: 函数参数过多
```python
async def create_event(
    self,
    user_id: int,
    event_type: str,
    title: str,
    description: str,
    event_date: datetime,
    impact_score: int,
    related_stocks: List[str],
    source: str,
    source_url: str
):
```

**重构方案**:
```python
@dataclass
class CreateEventRequest:
    event_type: str
    title: str
    description: str
    event_date: datetime
    impact_score: int
    related_stocks: List[str]
    source: str
    source_url: str

async def create_event(self, user_id: int, request: CreateEventRequest):
    pass
```

---

#### 4. 策略模式引入

**位置**: `backend/app/services/export/export_service.py`

**问题**: 大量 if-else 分支
```python
def export(self, data, format):
    if format == "csv":
        # 50行 CSV 导出逻辑
    elif format == "excel":
        # 50行 Excel 导出逻辑
    elif format == "pdf":
        # 50行 PDF 导出逻辑
```

**重构方案**:
```python
# 策略接口
class ExportStrategy(ABC):
    @abstractmethod
    def export(self, data) -> bytes:
        pass

class CsvExporter(ExportStrategy):
    def export(self, data) -> bytes:
        pass

class ExcelExporter(ExportStrategy):
    def export(self, data) -> bytes:
        pass

# 使用
exporters = {
    "csv": CsvExporter(),
    "excel": ExcelExporter(),
    "pdf": PdfExporter()
}

def export(self, data, format):
    return exporters[format].export(data)
```

---

### 🟢 低优先级优化

#### 5. 命名改进

| 位置 | 当前 | 建议 | 原因 |
|------|------|------|------|
| `service.py:30` | `d` | `data` | 含义不清 |
| `converter.py:45` | `calc_val` | `calculated_value` | 避免缩写 |
| `builder.py:20` | `res` | `response` | 一致性 |

#### 6. 魔法数字消除

**位置**: `backend/app/services/analysis/score_service.py:35`

```python
# 当前
if score > 80:
    return "优秀"
elif score > 60:
    return "良好"

# 建议
SCORE_EXCELLENT = 80
SCORE_GOOD = 60

if score > SCORE_EXCELLENT:
    return "优秀"
elif score > SCORE_GOOD:
    return "良好"
```

---

### 📋 重构路线图

#### 第一阶段（本周）
| 任务 | 文件 | 预计工时 | 风险 |
|------|------|----------|------|
| 拆分 analyze_portfolio | ai_service.py | 2h | 低 |
| 提取权限检查 | 多文件 | 1h | 低 |

#### 第二阶段（下周）
| 任务 | 文件 | 预计工时 | 风险 |
|------|------|----------|------|
| 引入参数对象 | create_service.py | 1h | 中 |
| 策略模式重构 | export_service.py | 3h | 中 |

#### 第三阶段（持续）
- 命名改进
- 魔法数字消除
- 注释完善

---

### ⚠️ 重构注意事项

1. **保持测试覆盖**: 重构前确保有测试
2. **小步提交**: 每个小改动单独提交
3. **运行检查**: 每次重构后运行 `check_architecture.py`
4. **保持功能**: 重构不改变外部行为

---

### 📚 参考资源

- 《重构：改善既有代码的设计》
- [Refactoring Guru](https://refactoring.guru/)
- Python 设计模式
```

## 使用示例
- `/refactor-suggest` - 分析整个代码库
- `/refactor-suggest backend/app/services/` - 分析 Service 层
- `/refactor-suggest backend/app/services/analysis/ai_service.py` - 分析特定文件
