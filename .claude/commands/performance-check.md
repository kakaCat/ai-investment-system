# 性能检查

分析代码中的性能问题和优化机会。

---

请对 $ARGUMENTS 进行性能检查：

## 检查范围
- 如果参数为空，检查关键模块
- 如果指定路径，检查该路径

## 检查维度

### 1. 数据库性能 (P0)

#### N+1 查询
- 循环中的数据库查询
- 未使用 JOIN 或预加载
- 关联数据逐条获取

#### 慢查询风险
- 缺少索引的查询条件
- 全表扫描
- 大数据量 ORDER BY

#### 连接管理
- 连接泄漏
- 未使用连接池
- 事务过长

### 2. 内存性能 (P1)

- 大列表一次性加载
- 未使用生成器
- 对象未及时释放
- 大字符串拼接

### 3. 计算性能 (P1)

- 重复计算
- 可缓存但未缓存
- 复杂度过高的算法
- 同步阻塞操作

### 4. I/O 性能 (P1)

- 未使用异步 I/O
- 串行请求可并行
- 文件操作未缓冲
- 网络请求未超时

### 5. 缓存使用 (P2)

- 热点数据未缓存
- 缓存策略不当
- 缓存穿透/雪崩风险

## 输出格式

```
## 性能检查报告

### 📊 检查概述
- **检查范围**: {路径}
- **性能风险**: [高/中/低]
- **优化潜力**: [大/中/小]

---

### 🔴 严重问题 (P0)

#### 问题 1: N+1 查询

**位置**: `backend/app/services/portfolio/list_service.py:35-42`

**问题代码**:
```python
accounts = await self.account_repo.get_all_by_user(user_id)
for account in accounts:
    # ❌ N+1 问题：每个账户单独查询持仓
    holdings = await self.holding_repo.get_by_account(account.id)
    account.holdings = holdings
```

**影响**:
- 10 个账户 = 11 次查询
- 100 个账户 = 101 次查询
- 响应时间线性增长

**修复方案**:
```python
# ✅ 批量查询 + 内存关联
accounts = await self.account_repo.get_all_by_user(user_id)
account_ids = [a.id for a in accounts]

# 一次查询所有持仓
all_holdings = await self.holding_repo.get_by_accounts(account_ids)

# 内存中关联
holdings_map = defaultdict(list)
for h in all_holdings:
    holdings_map[h.account_id].append(h)

for account in accounts:
    account.holdings = holdings_map[account.id]
```

**预期收益**: 查询次数从 N+1 降为 2

---

#### 问题 2: 缺少索引

**位置**: `backend/app/repositories/event_repo.py:28`

**问题代码**:
```python
# 按时间范围查询事件
events = await session.execute(
    select(Event)
    .where(Event.user_id == user_id)
    .where(Event.event_date >= start_date)
    .where(Event.event_date <= end_date)
    .order_by(Event.event_date.desc())
)
```

**问题**: `event_date` 列可能缺少索引

**检查 SQL**:
```sql
EXPLAIN ANALYZE SELECT * FROM events
WHERE user_id = 1
AND event_date >= '2024-01-01'
AND event_date <= '2024-12-31'
ORDER BY event_date DESC;
```

**修复方案**:
```sql
-- 添加复合索引
CREATE INDEX idx_events_user_date
ON events(user_id, event_date DESC);
```

---

### 🟡 中等问题 (P1)

#### 问题 3: 重复计算

**位置**: `backend/app/services/analysis/portfolio_service.py:50-80`

**问题**:
```python
def analyze(self, holdings):
    # 计算总价值
    total = sum(h.quantity * h.price for h in holdings)

    # 再次计算（重复）
    for h in holdings:
        weight = (h.quantity * h.price) / total  # ❌ 重复计算 h.quantity * h.price
```

**修复方案**:
```python
def analyze(self, holdings):
    # 一次计算，多次使用
    values = [(h, h.quantity * h.price) for h in holdings]
    total = sum(v for _, v in values)

    for h, value in values:
        weight = value / total
```

---

#### 问题 4: 串行可并行

**位置**: `backend/app/services/market/quote_service.py:25`

**问题代码**:
```python
# ❌ 串行获取多个股票报价
quotes = []
for symbol in symbols:
    quote = await self.fetch_quote(symbol)
    quotes.append(quote)
```

**修复方案**:
```python
# ✅ 并行获取
import asyncio

tasks = [self.fetch_quote(symbol) for symbol in symbols]
quotes = await asyncio.gather(*tasks)
```

**预期收益**: 10 个股票从 10s 降为 1s

---

### 🟢 优化建议 (P2)

#### 建议 1: 添加缓存

**场景**: 股票基本信息查询

**当前**: 每次从数据库查询
**建议**: Redis 缓存，TTL 1 小时

```python
from app.core.cache import cache

@cache(ttl=3600)
async def get_stock_info(symbol: str):
    return await self.stock_repo.get_by_symbol(symbol)
```

---

#### 建议 2: 分页查询

**位置**: `backend/app/services/event/list_service.py`

**当前**: 返回所有事件
**风险**: 数据量大时内存溢出

**建议**:
```python
async def list_events(self, user_id: int, page: int = 1, size: int = 20):
    return await self.event_repo.paginate(
        user_id=user_id,
        page=page,
        size=size
    )
```

---

### 📈 性能指标建议

#### 需要监控的指标
| 指标 | 阈值 | 监控方式 |
|------|------|----------|
| API P99 延迟 | < 500ms | APM |
| 数据库查询时间 | < 100ms | Slow query log |
| 内存使用 | < 80% | Prometheus |
| 连接池使用率 | < 70% | 数据库监控 |

#### 添加性能日志
```python
import time
import logging

async def execute(self, request, user_id):
    start = time.time()

    result = await self._do_work()

    elapsed = time.time() - start
    if elapsed > 1.0:  # 超过1秒记录警告
        logging.warning(f"Slow operation: {elapsed:.2f}s")

    return result
```

---

### 📋 优化优先级

#### 立即优化（性能收益大）
1. [ ] 修复 N+1 查询 - `portfolio/list_service.py`
2. [ ] 添加索引 - `events.event_date`
3. [ ] 并行化外部调用 - `quote_service.py`

#### 计划优化
4. [ ] 添加 Redis 缓存
5. [ ] 实现分页查询
6. [ ] 消除重复计算

---

### 🔧 性能测试建议

```bash
# 使用 locust 进行负载测试
locust -f tests/performance/locustfile.py

# 使用 py-spy 进行性能分析
py-spy record -o profile.svg -- python app.py

# 数据库慢查询日志
SET log_min_duration_statement = 100;  -- 记录超过100ms的查询
```
```

## 使用示例
- `/performance-check` - 检查关键模块
- `/performance-check backend/app/services/` - 检查所有 Service
- `/performance-check backend/app/services/portfolio/` - 检查投资组合模块
