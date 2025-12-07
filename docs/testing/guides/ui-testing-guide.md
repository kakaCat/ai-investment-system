# UI自动化测试指南

> Playwright E2E测试完整指南

---

## 📐 目录

1. [环境配置](#环境配置)
2. [测试脚本结构](#测试脚本结构)
3. [编写测试用例](#编写测试用例)
4. [页面对象模式](#页面对象模式)
5. [最佳实践](#最佳实践)
6. [调试技巧](#调试技巧)
7. [常见问题](#常见问题)

---

## 🔧 环境配置

### 安装依赖

```bash
# 安装Playwright
pip install playwright pytest-playwright

# 安装浏览器驱动
playwright install chromium
```

### 项目结构

```
backend/tests/ui/
├── scripts/
│   ├── comprehensive_ui_test.py   # 综合UI测试
│   ├── modal_interaction_test.py  # 模态框交互测试
│   └── page_objects/              # 页面对象（推荐）
│       ├── login_page.py
│       ├── account_page.py
│       └── ...
├── screenshots/                   # 测试截图输出
└── config.py                      # 测试配置
```

### 配置文件示例

```python
# backend/tests/ui/config.py
class TestConfig:
    BASE_URL = "http://localhost:5175"
    API_URL = "http://localhost:8000"
    TIMEOUT = 30000  # 30秒
    SCREENSHOT_DIR = "./screenshots"

    # 测试用户
    TEST_USER = {
        "username": "testuser",
        "password": "Test123456"
    }
```

---

## 📝 测试脚本结构

### 基础测试模板

```python
import asyncio
from playwright.async_api import async_playwright, Page

async def run_tests():
    async with async_playwright() as p:
        # 1. 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 2. 执行测试
            await test_login(page)
            await test_dashboard(page)

        finally:
            # 3. 清理资源
            await context.close()
            await browser.close()

async def test_login(page: Page):
    """测试登录功能"""
    print("\\n=== 测试: 登录功能 ===")

    # 导航到登录页面
    await page.goto("http://localhost:5175/login")

    # 填写表单
    await page.fill('input[type="text"]', "testuser")
    await page.fill('input[type="password"]', "Test123456")

    # 提交登录
    await page.click('button[type="submit"]')

    # 等待跳转
    await page.wait_for_url("**/dashboard")

    # 验证登录成功
    await page.wait_for_selector('.user-profile')

    print("✅ 登录成功")

if __name__ == "__main__":
    asyncio.run(run_tests())
```

---

## ✍️ 编写测试用例

### 1. 页面导航测试

```python
async def test_navigation(page: Page):
    """测试页面导航"""
    # 点击导航菜单
    await page.click('a[href="/accounts"]')

    # 等待URL变化
    await page.wait_for_url("**/accounts")

    # 验证页面标题
    title = await page.title()
    assert "账户管理" in title

    # 验证页面内容加载
    await page.wait_for_selector('.account-list')
```

### 2. 表单填写测试

```python
async def test_create_account_form(page: Page):
    """测试账户创建表单"""
    # 点击创建按钮
    await page.click('button:has-text("添加账户")')

    # 等待模态框出现
    await page.wait_for_selector('.el-dialog')

    # 填写表单
    await page.fill('input[placeholder="账户名称"]', "测试账户")
    await page.select_option('select[name="account_type"]', "a_share")
    await page.fill('input[name="initial_balance"]', "100000")

    # 提交表单
    await page.click('button:has-text("确定")')

    # 等待成功提示
    await page.wait_for_selector('.el-message--success')

    print("✅ 表单提交成功")
```

### 3. 列表查询测试

```python
async def test_account_list(page: Page):
    """测试账户列表查询"""
    await page.goto("http://localhost:5175/accounts")

    # 等待列表加载
    await page.wait_for_selector('.account-list')

    # 获取列表项数量
    items = await page.query_selector_all('.account-item')
    print(f"找到 {len(items)} 个账户")

    # 验证列表不为空
    assert len(items) > 0, "账户列表为空"

    # 点击第一个账户
    await items[0].click()

    # 等待详情页加载
    await page.wait_for_selector('.account-detail')
```

### 4. API调用测试

```python
async def test_api_call(page: Page):
    """测试页面API调用"""
    # 监听API请求
    async with page.expect_response(
        lambda response: "/api/v1/account/query" in response.url
    ) as response_info:
        # 触发API调用
        await page.click('button:has-text("刷新")')

    response = await response_info.value

    # 验证响应状态
    assert response.status == 200

    # 验证响应数据
    data = await response.json()
    assert data["code"] == 0
    assert "data" in data

    print(f"✅ API调用成功: {response.url}")
```

### 5. 错误处理测试

```python
async def test_validation_error(page: Page):
    """测试表单验证"""
    # 提交空表单
    await page.click('button:has-text("添加账户")')
    await page.wait_for_selector('.el-dialog')
    await page.click('button:has-text("确定")')

    # 验证错误提示
    error_msg = await page.wait_for_selector('.el-form-item__error')
    text = await error_msg.text_content()
    assert "必填" in text or "不能为空" in text

    print("✅ 表单验证生效")
```

---

## 🏗️ 页面对象模式 (POM)

### 为什么使用POM？

- ✅ 提高代码复用性
- ✅ 降低维护成本
- ✅ 提高测试可读性
- ✅ 隔离UI变化影响

### 页面对象示例

```python
# backend/tests/ui/page_objects/login_page.py
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = 'input[type="text"]'
        self.password_input = 'input[type="password"]'
        self.login_button = 'button[type="submit"]'

    async def goto(self):
        """导航到登录页"""
        await self.page.goto("http://localhost:5175/login")

    async def login(self, username: str, password: str):
        """执行登录操作"""
        await self.page.fill(self.username_input, username)
        await self.page.fill(self.password_input, password)
        await self.page.click(self.login_button)

    async def is_logged_in(self) -> bool:
        """检查是否登录成功"""
        try:
            await self.page.wait_for_selector('.user-profile', timeout=5000)
            return True
        except:
            return False
```

```python
# backend/tests/ui/page_objects/account_page.py
class AccountPage:
    def __init__(self, page: Page):
        self.page = page
        self.add_button = 'button:has-text("添加账户")'
        self.account_list = '.account-list'
        self.dialog = '.el-dialog'

    async def goto(self):
        """导航到账户页面"""
        await self.page.goto("http://localhost:5175/accounts")
        await self.page.wait_for_selector(self.account_list)

    async def get_account_count(self) -> int:
        """获取账户数量"""
        items = await self.page.query_selector_all('.account-item')
        return len(items)

    async def open_create_dialog(self):
        """打开创建账户对话框"""
        await self.page.click(self.add_button)
        await self.page.wait_for_selector(self.dialog)

    async def create_account(self, name: str, account_type: str, balance: float):
        """创建新账户"""
        await self.open_create_dialog()
        await self.page.fill('input[placeholder="账户名称"]', name)
        await self.page.select_option('select[name="account_type"]', account_type)
        await self.page.fill('input[name="initial_balance"]', str(balance))
        await self.page.click('button:has-text("确定")')
        await self.page.wait_for_selector('.el-message--success')
```

### 使用页面对象

```python
async def test_with_page_objects():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 使用LoginPage
            login_page = LoginPage(page)
            await login_page.goto()
            await login_page.login("testuser", "Test123456")
            assert await login_page.is_logged_in()

            # 使用AccountPage
            account_page = AccountPage(page)
            await account_page.goto()
            count_before = await account_page.get_account_count()

            await account_page.create_account(
                name="新账户",
                account_type="a_share",
                balance=100000.0
            )

            count_after = await account_page.get_account_count()
            assert count_after == count_before + 1

        finally:
            await browser.close()
```

---

## ✅ 最佳实践

### 1. 使用有意义的等待

```python
# ❌ 不好: 固定等待
await asyncio.sleep(3)

# ✅ 好: 等待特定条件
await page.wait_for_selector('.account-list')
await page.wait_for_url("**/dashboard")
await page.wait_for_load_state("networkidle")
```

### 2. 使用稳定的选择器

```python
# ❌ 不好: 依赖位置和样式
await page.click('.el-button.is-primary')

# ✅ 好: 使用语义化选择器
await page.click('button[data-testid="create-account"]')
await page.click('button:has-text("添加账户")')
await page.click('a[href="/accounts"]')
```

### 3. 截图和调试

```python
async def test_with_screenshot(page: Page):
    try:
        # 执行测试操作
        await page.goto("http://localhost:5175/accounts")

        # 成功时截图
        await page.screenshot(path="screenshots/accounts_page.png")

    except Exception as e:
        # 失败时截图
        await page.screenshot(path="screenshots/error_screenshot.png")
        raise e
```

### 4. 测试数据隔离

```python
# 使用唯一标识符
import time

async def test_create_account():
    unique_name = f"测试账户_{int(time.time())}"

    await account_page.create_account(
        name=unique_name,
        account_type="a_share",
        balance=100000.0
    )

    # 清理: 删除测试账户
    await account_page.delete_account(unique_name)
```

### 5. 并发测试注意事项

```python
# 为每个测试创建独立的浏览器上下文
async def test_concurrent():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # 创建多个独立上下文
        context1 = await browser.new_context()
        context2 = await browser.new_context()

        page1 = await context1.new_page()
        page2 = await context2.new_page()

        # 并发执行
        await asyncio.gather(
            test_scenario_1(page1),
            test_scenario_2(page2)
        )

        await browser.close()
```

---

## 🐛 调试技巧

### 1. 启用调试模式

```python
# 非Headless模式运行
browser = await p.chromium.launch(
    headless=False,
    slow_mo=500  # 每步操作延迟500ms
)
```

### 2. 打印页面信息

```python
# 打印当前URL
print(f"当前URL: {page.url}")

# 打印页面标题
print(f"页面标题: {await page.title()}")

# 打印元素文本
element = await page.query_selector('.error-message')
if element:
    print(f"错误信息: {await element.text_content()}")
```

### 3. 监听控制台输出

```python
def handle_console(msg):
    print(f"浏览器控制台: {msg.text}")

page.on("console", handle_console)
```

### 4. 保存网络请求日志

```python
async def log_requests(page: Page):
    async def handle_request(request):
        if "/api/" in request.url:
            print(f"API请求: {request.method} {request.url}")

    async def handle_response(response):
        if "/api/" in response.url:
            print(f"API响应: {response.status} {response.url}")

    page.on("request", handle_request)
    page.on("response", handle_response)
```

---

## ❓ 常见问题

### Q1: 元素找不到 (Timeout)

**问题**: `TimeoutError: Timeout 30000ms exceeded`

**解决方案**:
1. 检查选择器是否正确
2. 增加超时时间
3. 确认元素是否动态加载
4. 使用`wait_for_selector`等待元素出现

```python
# 增加超时
await page.wait_for_selector('.account-list', timeout=60000)

# 检查元素是否存在
element = await page.query_selector('.account-list')
if element:
    print("元素存在")
else:
    print("元素不存在")
```

### Q2: 点击无效

**问题**: 点击按钮但没有反应

**解决方案**:
1. 确认元素是否可见
2. 等待元素可交互
3. 检查是否被其他元素遮挡

```python
# 等待元素可见
await page.wait_for_selector('button', state='visible')

# 滚动到元素位置
await page.locator('button').scroll_into_view_if_needed()

# 强制点击
await page.locator('button').click(force=True)
```

### Q3: 模态框关闭失败

**问题**: 模态框没有正确关闭

**解决方案**:
```python
# 等待模态框出现
await page.wait_for_selector('.el-dialog')

# 点击关闭按钮
await page.click('.el-dialog__close')

# 等待模态框消失
await page.wait_for_selector('.el-dialog', state='hidden')
```

### Q4: 登录测试失败

**问题**: 登录功能测试一直失败

**解决方案**:
1. 确认测试用户已创建
2. 检查密码是否正确
3. 查看后端日志确认认证流程

```bash
# 创建测试用户
python backend/scripts/seed_test_data.py
```

---

## 🔗 相关资源

### 内部文档
- [测试策略](../strategy/test-strategy.md)
- [当前测试报告](../reports/2025-11-19-ui-test-results.md)
- [测试覆盖率](../coverage/current-coverage.md)

### 外部资源
- [Playwright Python官方文档](https://playwright.dev/python/)
- [Playwright最佳实践](https://playwright.dev/python/docs/best-practices)
- [Playwright选择器指南](https://playwright.dev/python/docs/selectors)

---

## 📝 测试检查清单

运行UI测试前：

- [ ] 前端服务运行在 http://localhost:5175
- [ ] 后端服务运行在 http://localhost:8000
- [ ] 数据库已启动
- [ ] 测试用户已创建
- [ ] 测试数据已seed
- [ ] Playwright已安装
- [ ] 浏览器驱动已安装

---

**最后更新**: 2025-11-19
**维护者**: QA Team
