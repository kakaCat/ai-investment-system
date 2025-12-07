# 安全审计

全面检查代码中的安全漏洞和风险。

---

请对 $ARGUMENTS 进行安全审计：

## 审计范围
- 如果参数为空，审计整个 `backend/app/` 目录
- 如果指定路径，只审计该路径

## 审计维度

### 1. 注入攻击 (P0)

#### SQL 注入
- 原始 SQL 拼接
- 未参数化的查询
- 动态表名/列名

#### 命令注入
- os.system / subprocess 调用
- 未过滤的用户输入

#### XSS
- 未转义的 HTML 输出
- 动态 JavaScript 生成

### 2. 身份认证 (P0)

- 密码是否加密存储（bcrypt/argon2）
- Token 是否安全生成
- Session 管理是否安全
- 是否有暴力破解防护

### 3. 授权控制 (P0)

- 是否验证资源所有权（user_id 检查）
- 是否有越权访问风险
- API 是否有适当的权限检查
- 敏感操作是否有二次确认

### 4. 数据保护 (P1)

- 敏感数据是否加密（API Key、密码）
- 日志是否包含敏感信息
- 错误信息是否泄露内部结构
- 是否有数据脱敏处理

### 5. 输入验证 (P1)

- 参数类型校验
- 长度限制
- 格式验证
- 边界值检查

### 6. 配置安全 (P1)

- 硬编码的密钥/密码
- DEBUG 模式是否关闭
- CORS 配置是否过于宽松
- 敏感配置是否在环境变量

### 7. 依赖安全 (P2)

- 是否有已知漏洞的依赖
- 依赖版本是否过旧

## 输出格式

```
## 安全审计报告

### 📋 审计概述
- **审计范围**: {路径}
- **审计时间**: {时间}
- **代码行数**: X 行
- **风险等级**: [高危/中危/低危]

### 📊 风险统计
| 等级 | 数量 | 说明 |
|------|------|------|
| 🔴 高危 (P0) | X | 必须立即修复 |
| 🟡 中危 (P1) | X | 应尽快修复 |
| 🟢 低危 (P2) | X | 建议修复 |

---

### 🔴 高危漏洞 (P0)

#### 漏洞 1: SQL 注入风险
- **位置**: `backend/app/repositories/account_repo.py:42`
- **类型**: SQL 注入
- **风险**: 攻击者可执行任意 SQL，导致数据泄露或破坏
- **问题代码**:
```python
# 危险：直接拼接用户输入
query = f"SELECT * FROM accounts WHERE name = '{name}'"
```
- **修复方案**:
```python
# 安全：使用参数化查询
query = "SELECT * FROM accounts WHERE name = :name"
result = await session.execute(text(query), {"name": name})
```
- **参考**: OWASP SQL Injection Prevention

---

#### 漏洞 2: 越权访问风险
- **位置**: `backend/app/services/account/detail_service.py:25`
- **类型**: 授权控制
- **风险**: 用户可访问他人账户数据
- **问题代码**:
```python
# 危险：未验证资源所有权
account = await self.account_repo.get_by_id(account_id)
return AccountDetailConverter.convert(account)
```
- **修复方案**:
```python
# 安全：验证 user_id
account = await self.account_repo.get_by_id(account_id)
if account.user_id != user_id:
    raise PermissionError("无权访问此账户")
return AccountDetailConverter.convert(account)
```

---

### 🟡 中危漏洞 (P1)

#### 漏洞 3: 敏感信息日志
- **位置**: `backend/app/services/auth/login_service.py:50`
- **类型**: 数据保护
- **风险**: 密码可能被记录到日志
- **问题代码**:
```python
logger.info(f"Login attempt: {username}, {password}")
```
- **修复方案**:
```python
logger.info(f"Login attempt: {username}")
```

---

### 🟢 低危问题 (P2)

#### 问题 4: 依赖版本过旧
- **依赖**: `fastapi==0.68.0`
- **当前版本**: 0.68.0
- **最新版本**: 0.104.0
- **建议**: 升级到最新稳定版

---

### ✅ 安全最佳实践确认

已正确实现的安全措施：

1. ✅ 密码使用 bcrypt 加密
2. ✅ JWT Token 正确签名
3. ✅ CORS 配置合理
4. ✅ 敏感配置使用环境变量

---

### 📋 修复优先级

#### 立即修复（今天）
1. [ ] SQL 注入 - `account_repo.py:42`
2. [ ] 越权访问 - `detail_service.py:25`

#### 本周修复
3. [ ] 敏感信息日志 - `login_service.py:50`
4. [ ] 输入验证缺失 - `event_api.py:30`

#### 计划修复
5. [ ] 升级依赖版本

---

### 🔒 安全加固建议

1. **添加 Rate Limiting**: 防止暴力破解
2. **实现 CSRF 保护**: 防止跨站请求伪造
3. **添加安全头**: X-Content-Type-Options, X-Frame-Options
4. **定期安全扫描**: 集成到 CI/CD

---

### 📚 参考资源
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
```

## 使用示例
- `/security-audit` - 审计整个后端
- `/security-audit backend/app/api/` - 审计 API 层
- `/security-audit backend/app/services/auth/` - 审计认证模块
