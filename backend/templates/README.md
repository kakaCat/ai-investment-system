# 后端代码模板

> 标准化代码模板，确保架构一致性

---

## 📂 模板文件

| 模板文件 | 用途 | 对应层级 |
|---------|------|---------|
| `service_template.py` | Service + Converter + Builder | 业务逻辑层 |
| `api_template.py` | API Controller | 接口层 |
| `repository_template.py` | Repository | 数据访问层 |

---

## 🎯 使用流程

### 1. 开发新功能前

```bash
# 第1步: 阅读架构约束文档（必需）
cat backend/ARCHITECTURE.md

# 第2步: 选择合适的模板
# - 新增API? → api_template.py + service_template.py
# - 新增Service? → service_template.py
# - 新增Repository? → repository_template.py

# 第3步: 运行架构检查
python scripts/check_architecture.py
```

### 2. 使用模板创建代码

#### 示例：创建账户详情功能

```bash
# 1. 复制Service模板
cp backend/templates/service_template.py \
   backend/app/services/account/detail_service.py

# 2. 复制API模板
cp backend/templates/api_template.py \
   backend/app/api/v1/account_api.py

# 3. 复制Repository模板（如果需要新的Repository）
cp backend/templates/repository_template.py \
   backend/app/repositories/account_repo.py
```

#### 全局替换占位符

打开文件后，全局替换以下占位符：

**service_template.py**:
- `{Feature}` → `AccountDetail`
- `{Module}` → `account`
- `{Action}` → `detail`

**api_template.py**:
- `{Module}` → `Account` (首字母大写)
- `{module}` → `account` (小写)
- `{Feature}` → `AccountDetail`
- `{Action}` → `detail`

**repository_template.py**:
- `{Module}` → `Account`
- `{module}` → `account`
- `{table}` → `accounts`

---

## 📐 架构约束

### Service模板约束

✅ **必须遵守**:
1. 一个文件包含三个类: Service + Converter + Builder
2. 文件命名: `{action}_service.py`
3. Converter所有方法使用 `@staticmethod`
4. Builder所有方法使用 `@staticmethod`
5. Service负责: 权限检查 + 数据获取 + 调用Converter
6. Converter负责: 所有业务逻辑和计算
7. Builder负责: 构建响应数据结构

❌ **禁止**:
- Service中直接编写业务逻辑
- Converter中访问数据库
- Builder中进行业务计算
- 在任何地方使用实例方法（除了Service.__init__和execute）

### API模板约束

✅ **必须遵守**:
1. 所有API使用 POST 方法
2. URL格式: `/api/v1/{module}/{action}`
3. 编写完整的8段式文档注释
4. Controller只负责: 接收请求 → 调用Service → 返回响应
5. 完整的异常处理

❌ **禁止**:
- 使用 GET/PUT/DELETE/PATCH 方法
- 在Controller中编写业务逻辑
- 直接访问数据库

### Repository模板约束

✅ **必须遵守**:
1. 只提供纯粹的CRUD操作
2. 默认过滤软删除记录 (`is_deleted=False`)
3. 使用软删除（不物理删除）
4. 支持分页查询

❌ **禁止**:
- 在Repository中编写业务逻辑
- 在Repository中进行数据计算
- 在Repository中调用其他Repository
- 在Repository中进行数据格式化

---

## 🔍 示例代码

### 完整的三层架构示例

#### 1. Repository层（数据访问）

```python
# backend/app/repositories/account_repo.py
class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[Account]:
        stmt = select(Account).where(
            and_(
                Account.id == id,
                Account.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def query_by_user(self, user_id: int) -> List[Account]:
        stmt = select(Account).where(
            and_(
                Account.user_id == user_id,
                Account.is_deleted == False
            )
        ).order_by(desc(Account.created_at))
        result = await self.db.execute(stmt)
        return result.scalars().all()
```

#### 2. Service层（业务编排）

```python
# backend/app/services/account/detail_service.py
class AccountDetailService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.holding_repo = HoldingRepository(db)

    async def execute(self, request: dict, user_id: int) -> dict:
        # 1. 权限检查
        account = await self.account_repo.get_by_id(request["account_id"])
        if not account or account.user_id != user_id:
            raise PermissionError("无权访问此账户")

        # 2. 获取数据
        holdings = await self.holding_repo.query_by_account(account.id)

        # 3. 调用Converter处理业务逻辑
        return AccountDetailConverter.convert(account, holdings)


class AccountDetailConverter:
    @staticmethod
    def convert(account, holdings: list) -> dict:
        # 业务计算
        total_value = AccountDetailConverter._calculate_total_value(holdings)
        profit_loss = AccountDetailConverter._calculate_profit_loss(holdings)

        # 调用Builder构建响应
        return AccountDetailBuilder.build_response(
            account=account,
            holdings=holdings,
            total_value=total_value,
            profit_loss=profit_loss
        )

    @staticmethod
    def _calculate_total_value(holdings: list) -> float:
        return sum(h.quantity * h.current_price for h in holdings)

    @staticmethod
    def _calculate_profit_loss(holdings: list) -> float:
        return sum(
            (h.current_price - h.cost_price) * h.quantity
            for h in holdings
        )


class AccountDetailBuilder:
    @staticmethod
    def build_response(**kwargs) -> dict:
        return {
            "account": {
                "id": kwargs["account"].id,
                "name": kwargs["account"].name,
                "type": kwargs["account"].account_type.value
            },
            "stats": {
                "total_value": kwargs["total_value"],
                "profit_loss": kwargs["profit_loss"],
                "return_rate": kwargs["profit_loss"] / kwargs["total_value"] * 100
                    if kwargs["total_value"] > 0 else 0
            },
            "holdings": [
                {
                    "stock_code": h.stock_code,
                    "quantity": h.quantity,
                    "cost_price": float(h.cost_price),
                    "current_price": float(h.current_price)
                }
                for h in kwargs["holdings"]
            ]
        }
```

#### 3. API层（接口）

```python
# backend/app/api/v1/account_api.py
@router.post("/detail")
async def get_account_detail(
    request: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    查询账户详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/detail
    对应页面: pages/account/detail.vue
    接口功能: 查询账户详细信息，包括持仓和统计数据

    ========================================
    请求参数
    ========================================
    {
        "account_id": 123    # 账户ID（必需）
    }

    ========================================
    响应数据
    ========================================
    {
        "code": 0,
        "message": "success",
        "data": {
            "account": {
                "id": 123,
                "name": "我的A股账户",
                "type": "a_share"
            },
            "stats": {
                "total_value": 100000.00,
                "profit_loss": 5000.00,
                "return_rate": 5.00
            },
            "holdings": [...]
        }
    }

    ========================================
    执行流程
    ========================================
    1. 接收请求参数
    2. 获取当前用户
    3. 创建Service实例
    4. 调用Service执行业务逻辑
    5. 返回响应数据

    ========================================
    修改记录
    ========================================
    2025-11-19: 初始版本
    """
    try:
        service = AccountDetailService(db)
        result = await service.execute(request, user.id)
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

---

## ✅ 开发检查清单

### 开发前

- [ ] 已阅读 `backend/ARCHITECTURE.md`
- [ ] 已选择合适的模板
- [ ] 已了解业务需求

### 开发中

- [ ] 使用模板创建文件
- [ ] 替换所有占位符
- [ ] 实现业务逻辑（填充TODO）
- [ ] 编写完整的文档注释

### 开发后

- [ ] 运行架构检查: `python scripts/check_architecture.py`
- [ ] 检查所有Converter方法是否有 `@staticmethod`
- [ ] 检查所有Builder方法是否有 `@staticmethod`
- [ ] 检查API是否使用POST方法
- [ ] 检查是否有8段式文档注释
- [ ] 手动测试功能
- [ ] 添加单元测试

---

## 🚨 常见错误

### 错误1: Converter方法没有@staticmethod

❌ **错误**:
```python
class AccountDetailConverter:
    def convert(self, data):  # ❌ 缺少 @staticmethod
        return self._calculate(data)
```

✅ **正确**:
```python
class AccountDetailConverter:
    @staticmethod
    def convert(data):  # ✅ 使用 @staticmethod
        return AccountDetailConverter._calculate(data)
```

### 错误2: 在Controller中编写业务逻辑

❌ **错误**:
```python
@router.post("/detail")
async def get_account_detail(request: dict, ...):
    # ❌ 在Controller中计算
    account = await account_repo.get_by_id(request["account_id"])
    total = sum(h.quantity * h.price for h in account.holdings)
    return {"total": total}
```

✅ **正确**:
```python
@router.post("/detail")
async def get_account_detail(request: dict, ...):
    # ✅ 调用Service
    service = AccountDetailService(db)
    result = await service.execute(request, user.id)
    return {"data": result}
```

### 错误3: 在Repository中编写业务逻辑

❌ **错误**:
```python
class AccountRepository:
    async def get_total_value(self, user_id: int):
        # ❌ Repository中进行业务计算
        accounts = await self.query_by_user(user_id)
        return sum(a.balance for a in accounts)
```

✅ **正确**:
```python
# Repository只负责查询
class AccountRepository:
    async def query_by_user(self, user_id: int):
        return await self.db.execute(...)

# Converter负责计算
class AccountSummaryConverter:
    @staticmethod
    def calculate_total_value(accounts: list) -> float:
        return sum(a.balance for a in accounts)
```

---

## 🔗 相关文档

- [后端架构约束](../ARCHITECTURE.md)
- [数据库设计规范](../../docs/design/database/schema-v1.md)
- [开发工作流程](~/.claude/CLAUDE.md#-开发流程规范)
- [架构检查脚本](../../scripts/check_architecture.py)

---

**最后更新**: 2025-11-19
**维护者**: Backend Team
