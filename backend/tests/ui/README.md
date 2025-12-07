# UI自动化测试

> 基于Playwright的前端E2E自动化测试

---

## 📂 目录结构

```
ui/
├── README.md              # 本文件 - UI测试说明
├── scripts/               # 测试脚本
│   ├── comprehensive_ui_test.py    # 综合UI测试（12模块）
│   └── modal_interaction_test.py   # 模态框交互测试（8套件）
├── screenshots/           # 测试截图（自动生成）
│   ├── ui_test_01_login.png
│   ├── ui_test_02_dashboard.png
│   └── ...
└── reports/               # 测试报告（待生成）
```

---

## 🎯 测试脚本说明

### 1. comprehensive_ui_test.py - 综合UI测试

**测试范围**:

| 模块 | 测试内容 | 状态 |
|------|----------|------|
| 模块1 | 登录流程测试（页面加载、表单元素、登录功能） | ✅ |
| 模块2 | Dashboard主页（导航栏、统计卡片、API调用） | ✅ |
| 模块3 | 账户管理页面 | ✅ |
| 模块4 | 持仓管理页面 | ✅ |
| 模块5 | 交易记录页面 | ✅ |
| 模块6 | 事件中心页面 | ✅ |
| 模块7 | AI分析页面 | ✅ |
| 模块8 | 系统设置页面 | ✅ |
| 模块9 | 消息通知测试（ElMessage） | ✅ |
| 模块10 | 下拉选择器测试（el-select） | ✅ |
| 模块11 | 控制台日志检查 | ✅ |
| 模块12 | API调用统计 | ✅ |

**运行方式**:
```bash
cd tests/ui/scripts
python comprehensive_ui_test.py
```

**最新结果** (2025-11-19):
```
✅ 通过率: 81.2% (13/16)
✅ API成功: 19/23
✅ 控制台错误: 0个
⏱️  耗时: ~25秒
📸 截图: 10张
```

---

### 2. modal_interaction_test.py - 模态框交互测试

**测试范围**:

| 套件 | 测试内容 | 状态 |
|------|----------|------|
| 套件1 | 账户管理表单弹框（添加/编辑） | ⏭️ 待前端实现 |
| 套件2 | 交易记录表单弹框（记录/导入） | ⏭️ 待前端实现 |
| 套件3 | 事件管理表单弹框 | ⏭️ 待前端实现 |
| 套件4 | AI分析相关弹框（单股/组合） | ⏭️ 待前端实现 |
| 套件5 | 确认对话框（ElMessageBox） | ⏭️ 待前端实现 |
| 套件6 | 消息通知（ElMessage） | ✅ |
| 套件7 | 下拉选择器交互（el-select/date-picker） | ⏭️ 待前端实现 |
| 套件8 | 其他交互组件（radio/checkbox/switch） | ⏭️ 待前端实现 |

**运行方式**:
```bash
cd tests/ui/scripts
python modal_interaction_test.py
```

**最新结果** (2025-11-19):
```
✅ 登录成功
⏭️  14个测试跳过（UI组件未实现）
⏱️  耗时: ~40秒
```

---

## 🚀 快速开始

### 环境准备

1. **安装依赖**:
```bash
# 安装Playwright
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

2. **启动服务**:
```bash
# 后端（终端1）
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（终端2）
cd frontend
npm run dev
```

3. **确认服务**:
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问
open http://localhost:5175
```

### 运行测试

```bash
# 进入测试目录
cd tests/ui/scripts

# 运行综合测试
python comprehensive_ui_test.py

# 运行模态框测试
python modal_interaction_test.py
```

---

## 📊 测试结果详解

### 通过的测试 ✅

1. **登录页面** - 页面标题、表单元素完整性
2. **页面导航** - 所有8个主要页面可正常访问
3. **API调用** - 无401认证错误，19/23接口成功
4. **控制台检查** - 无JavaScript错误（CORS已修复）
5. **组件加载** - ElMessage组件正常加载

### 失败的测试 ❌

1. **登录功能** - OAuth2表单认证流程待优化
2. **Dashboard导航栏识别** - CSS选择器需调整
3. **Dashboard统计卡片** - 元素识别待优化

### 跳过的测试 ⏭️

所有模态框和表单交互测试因前端未实现相应按钮而跳过，包括：
- 添加/编辑账户按钮
- 记录/导入交易按钮
- 添加事件按钮
- AI分析触发按钮
- 删除确认对话框
- 高级表单组件（日期选择器、单选框等）

---

## 📸 截图说明

测试过程中自动生成的截图保存在 `screenshots/` 目录：

| 截图 | 说明 | 大小 |
|------|------|------|
| ui_test_01_login.png | 登录页面 | 698KB |
| ui_test_02_dashboard.png | Dashboard主页 | 153KB |
| ui_test_03_accounts.png | 账户管理（显示3个账户） | 163KB |
| ui_test_04_holdings.png | 持仓管理 | 219KB |
| ui_test_05_trades.png | 交易记录 | 143KB |
| ui_test_06_events.png | 事件中心 | 182KB |
| ui_test_07_ai.png | AI分析 | 125KB |
| ui_test_08_settings.png | 系统设置 | 68KB |
| ui_test_09_messages.png | 消息通知组件 | 153KB |
| ui_test_10_selectors.png | 下拉选择器（空页面） | 8.3KB |

---

## 🔧 测试脚本架构

### TestResults类

负责收集和统计测试结果：

```python
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0

    def add_test(self, name, status, details=""):
        # 记录测试结果

    def print_summary(self):
        # 打印测试摘要
```

### 测试流程

1. **初始化** - 启动Playwright浏览器
2. **登录** - 自动填写表单并登录
3. **导航测试** - 依次访问各个页面
4. **截图** - 每个页面自动截图
5. **验证** - 检查元素存在性、API调用状态
6. **报告** - 生成详细测试报告

### 关键功能

- **控制台监听**: 捕获所有console日志
- **API拦截**: 记录所有API请求和响应
- **智能等待**: 使用networkidle等待页面加载完成
- **错误恢复**: 异常捕获，继续执行后续测试

---

## 🐛 调试指南

### 查看测试日志

测试过程中的所有输出都显示在控制台：
```bash
python comprehensive_ui_test.py 2>&1 | tee test_output.log
```

### 调试模式

修改脚本启用有头模式（显示浏览器窗口）：
```python
# 将 headless=True 改为 headless=False
browser = p.chromium.launch(headless=False)
```

### 常见问题

**Q: 登录失败怎么办？**
A: 确认后端服务运行正常，检查CORS配置是否包含前端端口

**Q: 截图为空白？**
A: 增加等待时间：`time.sleep(2)` 或使用 `page.wait_for_selector()`

**Q: 找不到元素？**
A: 使用 `page.locator().count()` 检查元素是否存在，调整CSS选择器

---

## 📈 改进计划

### 短期 (1-2周)

- [ ] 修复登录功能测试
- [ ] 优化Dashboard元素识别
- [ ] 添加更多断言验证

### 中期 (1个月)

- [ ] 等待前端实现模态框按钮后完善测试
- [ ] 添加表单填写和提交测试
- [ ] 实现测试数据自动清理

### 长期 (2-3个月)

- [ ] 集成到CI/CD流程
- [ ] 生成HTML测试报告
- [ ] 添加性能测试指标
- [ ] 实现并行测试执行

---

## 🔗 相关资源

- [Playwright官方文档](https://playwright.dev/python/)
- [Element Plus组件文档](https://element-plus.org/)
- [项目前端代码](../../frontend/)
- [项目后端代码](../../backend/)

---

**最后更新**: 2025-11-19
**维护者**: AI Development Team
**问题反馈**: 在项目Issue中提出
