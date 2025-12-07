# 后端开发架构约束

⚠️ **开发前必读** - 违反架构将无法通过Code Review和CI检查

---

## 📐 强制阅读文档

开发任何后端功能前，必须阅读以下文档：

1. [后端架构总览](../docs/design/architecture/backend-architecture.md) ⭐
2. [数据库设计规范](../docs/design/database/schema-v1.md) ⭐
3. [API设计规范](../docs/design/architecture/backend-architecture.md#api设计规范) ⭐

**为什么必须阅读**？
- 避免写出不符合架构的代码
- 避免重构返工浪费时间
- 确保代码能通过CI/CD检查
- 确保团队代码风格一致

---

## ✅ 开发前检查清单

### 新增API前

- [ ] 已阅读后端架构文档
- [ ] 确认使用 **POST方法**（不使用GET/PUT/DELETE）
- [ ] URL格式: `/api/v1/{module}/{action}`
  - ✅ 正确: `/api/v1/account/query`
  - ❌ 错误: `/api/v1/accounts` 或 `/api/v1/account/:id`
- [ ] 按照完整分层结构:
  ```
  Controller → Service → Converter → Builder → Repository → Database
  ```
- [ ] 编写完整的8段式API文档注释（见下方模板）
- [ ] 添加单元测试 (tests/unit/backend/)
- [ ] 添加集成测试 (tests/integration/)

### 新增数据库表前

- [ ] 已阅读数据库设计规范
- [ ] 使用 `BIGSERIAL` 主键（不使用UUID）
- [ ] 添加 `user_id` + `account_id`（如果业务需要账户隔离）
- [ ] 使用 PostgreSQL `ENUM` 定义状态字段
- [ ] 添加软删除字段（`is_deleted`, `deleted_at`）
- [ ] 添加审计字段（`created_at`, `updated_at`, `created_by`, `updated_by`）
- [ ] 使用 `NUMERIC(20,8)` 存储金额（不使用FLOAT）
- [ ] 所有时间使用 `TIMESTAMPTZ`（UTC时区）
- [ ] 添加唯一约束: `idempotency_key` (如果需要幂等性)
- [ ] 不使用数据库级外键（使用虚拟外键+索引）

### 新增Service前

- [ ] 文件命名: `{action}_service.py`
  - ✅ 正确: `account_detail_service.py`
  - ❌ 错误: `account_service.py` 或 `detail.py`
- [ ] 包含三个类: `Service` + `Converter` + `Builder`
- [ ] Converter所有方法使用 `@staticmethod`
- [ ] Builder所有方法使用 `@staticmethod`
- [ ] Service只负责:
  - 权限检查
  - 调用Repository
  - 调用Converter
  - 事务管理
- [ ] 业务逻辑全部在Converter中（不在Service或Repository）

---

## ❌ 常见违反示例

### 错误1: 使用GET/PUT/DELETE方法

```python
# ❌ 错误
@router.get("/account/detail")
async def get_account_detail(account_id: int):
    pass

# ❌ 错误
@router.put("/account/{id}")
async def update_account(id: int, data: dict):
    pass

# ✅ 正确
@router.post("/account/detail")
async def get_account_detail(request: dict, user: User = Depends(get_current_user)):
    pass

@router.post("/account/update")
async def update_account(request: dict, user: User = Depends(get_current_user)):
    pass
```

### 错误2: Controller中包含业务逻辑

```python
# ❌ 错误 - Controller中计算业务逻辑
@router.post("/account/detail")
async def get_account_detail(request: dict):
    account = await account_repo.get_by_id(request["account_id"])
    holdings = await holding_repo.query_by_account(account.id)

    # ❌ 业务计算不应在Controller
    total_value = sum(h.quantity * h.price for h in holdings)
    profit_loss = total_value - sum(h.quantity * h.cost for h in holdings)

    return {"account": account, "total_value": total_value}
```

```python
# ✅ 正确 - Controller只负责接收和返回
@router.post("/account/detail")
async def get_account_detail(
    request: dict,
    user: User = Depends(get_current_user)
):
    """
    [完整的8段式文档注释]
    """
    service = AccountDetailService()
    result = await service.execute(request, user.id)
    return result
```

### 错误3: Converter不是静态方法

```python
# ❌ 错误
class AccountDetailConverter:
    def convert(self, account, holdings):  # ❌ 缺少 @staticmethod
        total = self._calculate_total(holdings)
        return total
```

```python
# ✅ 正确
class AccountDetailConverter:
    @staticmethod
    def convert(account, holdings):
        total = AccountDetailConverter._calculate_total(holdings)
        return AccountDetailBuilder.build_response(account, total)

    @staticmethod
    def _calculate_total(holdings) -> float:
        return sum(h.quantity * h.price for h in holdings)
```

### 错误4: Service中包含业务逻辑

```python
# ❌ 错误 - Service中计算
class AccountDetailService:
    async def execute(self, request: dict, user_id: int):
        account = await self.account_repo.get_by_id(request["account_id"])
        holdings = await self.holding_repo.query_by_account(account.id)

        # ❌ 业务逻辑不应在Service
        total = sum(h.quantity * h.price for h in holdings)

        return {"total": total}
```

```python
# ✅ 正确 - Service只负责编排
class AccountDetailService:
    async def execute(self, request: dict, user_id: int):
        # 1. 权限检查
        account = await self.account_repo.get_by_id(request["account_id"])
        if account.user_id != user_id:
            raise PermissionError("无权访问此账户")

        # 2. 获取数据
        holdings = await self.holding_repo.query_by_account(account.id)

        # 3. 调用Converter处理业务逻辑
        return AccountDetailConverter.convert(account, holdings)
```

---

## ✅ 正确示例（完整）

### 完整Service文件示例

```python
"""
账户详情查询服务

相关文档:
- backend/ARCHITECTURE.md
- docs/design/architecture/backend-architecture.md
"""

from app.repositories.account_repo import AccountRepository
from app.repositories.holding_repo import HoldingRepository
from app.core.exceptions import PermissionError, NotFoundError


class AccountDetailService:
    """账户详情查询服务"""

    def __init__(self):
        self.account_repo = AccountRepository()
        self.holding_repo = HoldingRepository()

    async def execute(self, request: dict, user_id: int) -> dict:
        """执行账户详情查询"""
        account_id = request.get("account_id")
        if not account_id:
            raise ValueError("缺少account_id参数")

        # 1. 权限检查
        account = await self.account_repo.get_by_id(account_id)
        if not account:
            raise NotFoundError("账户不存在")
        if account.user_id != user_id:
            raise PermissionError("无权访问此账户")
        if account.is_deleted:
            raise NotFoundError("账户已删除")

        # 2. 获取数据
        holdings = await self.holding_repo.query_by_account(account_id)

        # 3. 调用Converter处理业务逻辑
        return AccountDetailConverter.convert(account, holdings)


class AccountDetailConverter:
    """
    业务逻辑转换器

    ⚠️ 所有方法必须是静态方法
    ⚠️ 所有业务计算在这里实现
    """

    @staticmethod
    def convert(account, holdings: list) -> dict:
        """转换账户详情数据"""
        total_value = AccountDetailConverter._calculate_total_value(holdings)
        total_cost = AccountDetailConverter._calculate_total_cost(holdings)
        profit_loss = total_value - total_cost
        profit_loss_pct = (profit_loss / total_cost * 100) if total_cost > 0 else 0.0

        return AccountDetailBuilder.build_response(
            account=account,
            holdings_count=len(holdings),
            total_value=total_value,
            total_cost=total_cost,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct
        )

    @staticmethod
    def _calculate_total_value(holdings: list) -> float:
        """计算总市值"""
        return sum(h.quantity * h.current_price for h in holdings)

    @staticmethod
    def _calculate_total_cost(holdings: list) -> float:
        """计算总成本"""
        return sum(h.quantity * h.cost_price for h in holdings)


class AccountDetailBuilder:
    """
    数据构建器

    ⚠️ 所有方法必须是静态方法
    ⚠️ 只负责数据组装，不包含业务逻辑
    """

    @staticmethod
    def build_response(account, holdings_count: int, **stats) -> dict:
        """构建API响应"""
        return {
            "account": {
                "account_id": account.id,
                "account_name": account.account_name,
                "market": account.market,
            },
            "stats": {
                "total_value": round(stats.get("total_value", 0.0), 2),
                "total_cost": round(stats.get("total_cost", 0.0), 2),
                "profit_loss": round(stats.get("profit_loss", 0.0), 2),
                "profit_loss_pct": round(stats.get("profit_loss_pct", 0.0), 2),
            },
            "holdings_count": holdings_count
        }
```

### Controller (API) 完整示例

```python
from fastapi import APIRouter, Depends
from app.services.account.account_detail_service import AccountDetailService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/detail")
async def get_account_detail(
    request: dict,
    user: User = Depends(get_current_user)
):
    """
    获取账户详情

    ========================================
    接口信息
    ========================================
    接口路径: POST /api/v1/account/detail
    对应页面: pages/account/detail.vue
    接口功能: 查询单个账户的详细信息

    ========================================
    请求参数
    ========================================
    {
        "account_id": 1  # int, 必需, 账户ID
    }

    ========================================
    响应数据
    ========================================
    {
        "account": {"account_id": 1, "account_name": "我的账户"},
        "stats": {"total_value": 150000.50},
        "holdings_count": 5
    }

    ========================================
    执行流程
    ========================================
    1. Controller 接收请求
    2. Service 查询账户（权限检查）
    3. Service 查询持仓
    4. Converter 计算统计
    5. Builder 构建响应

    ========================================
    业务规则
    ========================================
    1. 只能查询自己的账户
    2. 已删除账户不可查询

    ========================================
    错误码
    ========================================
    1001: 账户不存在
    1002: 无权访问

    ========================================
    前端调用
    ========================================
    const data = await post('/account/detail', {account_id: 1})

    ========================================
    修改记录
    ========================================
    2025-11-19: 初始版本
    """
    service = AccountDetailService()
    result = await service.execute(request, user.id)
    return result
```

---

## 🔍 架构自动检查

运行检查脚本：
```bash
python scripts/check_architecture.py
```

违反项将被自动检测：
- ❌ API使用GET/PUT/DELETE方法
- ❌ Service文件命名不规范
- ❌ Converter不是静态方法
- ❌ Builder不是静态方法

---

## 📁 目录结构规范

```
backend/app/
├── api/v1/
│   ├── account_api.py
│   ├── holding_api.py
│   └── trade_api.py
│
├── services/
│   ├── account/
│   │   ├── account_detail_service.py
│   │   ├── account_list_service.py
│   │   └── account_create_service.py
│   ├── holding/
│   └── trade/
│
├── repositories/
│   ├── account_repo.py
│   ├── holding_repo.py
│   └── trade_repo.py
│
└── models/
    ├── account.py
    ├── holding.py
    └── trade.py
```

---

## 🔗 相关资源

- [完整后端架构文档](../docs/design/architecture/backend-architecture.md)
- [数据库Schema设计](../docs/design/database/schema-v1.md)
- [Service层代码模板](templates/service_template.py)
- [全局架构守卫规范](~/.claude/CLAUDE.md#️-架构守卫规范)

---

**最后更新**: 2025-11-19
**维护者**: Backend Team
