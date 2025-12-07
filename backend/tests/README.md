# 测试目录

> 投资管理系统的所有测试内容

---

## 📐 目录结构

```
tests/
├── README.md           # 本文件 - 测试索引和说明
├── ui/                 # UI自动化测试
│   ├── scripts/        # 测试脚本
│   ├── screenshots/    # 测试截图
│   └── reports/        # 测试报告
├── integration/        # 集成测试（待开发）
└── unit/               # 单元测试（待开发）
```

---

## 🎯 测试类型

### 1. UI自动化测试 (tests/ui/)

**目的**: 使用Playwright进行前端全流程自动化测试

**测试脚本**:
- `comprehensive_ui_test.py` - 综合UI测试（12个模块）
- `modal_interaction_test.py` - 模态框交互测试（8个测试套件）

**如何运行**:
```bash
# 确保前后端服务已启动
# Backend: http://localhost:8000
# Frontend: http://localhost:5175

cd tests/ui/scripts
python comprehensive_ui_test.py    # 综合UI测试
python modal_interaction_test.py   # 模态框测试
```

**最新测试结果**:
- 综合UI测试: **81.2%** 通过率 (13/16)
- API调用成功: **19/23**
- 控制台错误: **0** 个
- 生成截图: **10** 张

**详细说明**: 见 [tests/ui/README.md](ui/README.md)

---

### 2. 集成测试 (tests/integration/)

**状态**: 🚧 待开发

**规划内容**:
- API端点集成测试
- 数据库操作测试
- 第三方服务集成测试（DeepSeek API, Tushare等）

---

### 3. 单元测试 (tests/unit/)

**状态**: 🚧 待开发

**规划内容**:
- Service层单元测试
- Converter/Builder单元测试
- Repository层单元测试
- 工具函数测试

---

## ✅ 测试检查清单

运行测试前确认：

- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端服务运行在 http://localhost:5175
- [ ] PostgreSQL数据库已启动
- [ ] 已安装Playwright: `pip install playwright && playwright install chromium`
- [ ] 测试用户已创建 (testuser/Test123456)

---

## 📊 测试覆盖范围

### UI测试覆盖

| 模块 | 状态 | 说明 |
|------|------|------|
| 登录流程 | ✅ | 页面加载、表单验证 |
| Dashboard | ✅ | 主页、统计卡片、API调用 |
| 账户管理 | ✅ | 页面导航、列表显示 |
| 持仓管理 | ✅ | 页面导航、数据展示 |
| 交易记录 | ✅ | 页面导航 |
| 事件中心 | ✅ | 页面导航 |
| AI分析 | ✅ | 页面导航 |
| 系统设置 | ✅ | 页面导航 |
| 消息通知 | ✅ | ElMessage组件 |
| 下拉选择器 | ✅ | el-select组件 |
| 模态框 | 🔄 | 待前端实现按钮后测试 |
| 表单交互 | 🔄 | 待前端实现后测试 |

### 待实现功能（测试已发现）

- ⏭️ 添加账户/编辑账户按钮
- ⏭️ 记录交易/导入交易按钮
- ⏭️ 添加事件按钮
- ⏭️ AI分析触发按钮
- ⏭️ 删除确认对话框
- ⏭️ 日期选择器
- ⏭️ 单选框/复选框/开关组件

---

## 🔄 测试更新记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-11-19 | v1.0 | 初始版本，完成UI自动化测试框架 |
| 2025-11-19 | v1.1 | 修复CORS问题，测试通过率提升至81.2% |

---

## 📝 最佳实践

1. **测试隔离**: 每个测试独立运行，不依赖其他测试
2. **截图记录**: 所有关键步骤自动截图，便于问题定位
3. **详细日志**: 记录API调用、控制台日志、测试时间
4. **失败重试**: 关键测试失败后自动重试一次
5. **定期清理**: 删除临时文件和过期截图

---

## 🔗 相关文档

- [UI测试详细说明](ui/README.md)
- [测试用例设计](../docs/design/testing/)
- [CI/CD集成](../docs/guides/deployment/ci-cd.md)

---

**最后更新**: 2025-11-19
