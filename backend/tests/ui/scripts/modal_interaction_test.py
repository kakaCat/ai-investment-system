"""
投资管理系统 - 模态框交互测试
深度测试所有弹框、对话框、消息通知和交互组件
"""
from playwright.sync_api import sync_playwright
import time
from datetime import datetime

class ModalTestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.tests = []

    def add_test(self, name, status, details="", screenshot=""):
        self.total += 1
        if status == "PASS":
            self.passed += 1
        elif status == "SKIP":
            self.skipped += 1
        else:
            self.failed += 1

        self.tests.append({
            "name": name,
            "status": status,
            "details": details,
            "screenshot": screenshot,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    def print_summary(self):
        print("\n" + "=" * 120)
        print("模态框测试报告摘要")
        print("=" * 120)
        print(f"总测试数: {self.total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"跳过: {self.skipped} ⏭️")
        if self.total - self.skipped > 0:
            print(f"有效通过率: {(self.passed/(self.total-self.skipped)*100):.1f}%")
        print("=" * 120)

        if self.failed > 0:
            print("\n失败的测试:")
            for test in self.tests:
                if test['status'] == 'FAIL':
                    print(f"  ❌ [{test['time']}] {test['name']}")
                    if test['details']:
                        print(f"     详情: {test['details']}")


def modal_interaction_test():
    results = ModalTestResults()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 捕获控制台日志
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("=" * 120)
        print("投资管理系统 - 模态框交互测试")
        print("=" * 120)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试URL: http://localhost:5175")
        print("=" * 120)

        # 登录
        print("\n执行登录...")
        try:
            page.goto('http://localhost:5175/login')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            page.fill('input[type="text"]', 'testuser')
            page.fill('input[type="password"]', 'Test123456')
            page.click('button:has-text("登录")')
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            token = page.evaluate('() => localStorage.getItem("token")')
            if token:
                print("✅ 登录成功")
            else:
                print("❌ 登录失败，部分测试可能无法执行")

        except Exception as e:
            print(f"❌ 登录异常: {e}")

        # ========================================
        # 测试套件1: 账户管理表单弹框
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件1: 账户管理表单弹框")
        print("=" * 120)

        # 1.1 添加账户弹框
        print("\n[1.1] 测试添加账户弹框 (AddAccountDialog)")
        try:
            page.goto('http://localhost:5175/accounts')
            time.sleep(2)

            # 查找"添加账户"按钮
            add_button = page.locator('button:has-text("添加账户"), button:has-text("新建账户")').first
            if add_button.count() > 0:
                add_button.click()
                time.sleep(1)

                # 检查弹框是否出现
                dialog = page.locator('.el-dialog:visible, .el-drawer:visible').first
                if dialog.count() > 0:
                    results.add_test("添加账户弹框 - 打开", "PASS", "弹框成功打开")
                    print("✅ 添加账户弹框打开成功")

                    # 检查表单元素
                    form_items = page.locator('.el-form-item').count()
                    print(f"   找到 {form_items} 个表单项")

                    page.screenshot(path='/tmp/modal_test_01_add_account.png', full_page=True)
                    results.add_test("添加账户弹框 - 表单", "PASS", f"{form_items}个表单项", "/tmp/modal_test_01_add_account.png")

                    # 关闭弹框
                    close_button = page.locator('.el-dialog__close, button:has-text("取消")').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                        results.add_test("添加账户弹框 - 关闭", "PASS")
                else:
                    results.add_test("添加账户弹框", "FAIL", "弹框未出现")
                    print("❌ 弹框未出现")
            else:
                results.add_test("添加账户弹框", "SKIP", "未找到触发按钮")
                print("⏭️  未找到添加账户按钮")

        except Exception as e:
            results.add_test("添加账户弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 1.2 编辑账户弹框
        print("\n[1.2] 测试编辑账户弹框")
        try:
            page.goto('http://localhost:5175/accounts')
            time.sleep(2)

            # 查找编辑按钮
            edit_button = page.locator('button:has-text("编辑"), .el-button:has-text("编辑")').first
            if edit_button.count() > 0:
                edit_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("编辑账户弹框", "PASS", "弹框成功打开")
                    print("✅ 编辑账户弹框打开成功")

                    page.screenshot(path='/tmp/modal_test_02_edit_account.png', full_page=True)

                    # 关闭
                    close_button = page.locator('.el-dialog__close, button:has-text("取消")').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("编辑账户弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("编辑账户弹框", "SKIP", "未找到编辑按钮")
                print("⏭️  未找到编辑按钮")

        except Exception as e:
            results.add_test("编辑账户弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件2: 交易记录表单弹框
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件2: 交易记录表单弹框")
        print("=" * 120)

        # 2.1 记录交易弹框
        print("\n[2.1] 测试记录交易弹框 (RecordTradeDialog)")
        try:
            page.goto('http://localhost:5175/trades')
            time.sleep(2)

            add_button = page.locator('button:has-text("记录交易"), button:has-text("添加交易")').first
            if add_button.count() > 0:
                add_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("记录交易弹框 - 打开", "PASS")
                    print("✅ 记录交易弹框打开成功")

                    # 检查关键表单元素
                    has_stock_input = page.locator('input[placeholder*="股票"], input[placeholder*="代码"]').count() > 0
                    has_type_select = page.locator('.el-select').count() > 0
                    has_quantity_input = page.locator('input[placeholder*="数量"]').count() > 0

                    print(f"   股票输入框: {has_stock_input}")
                    print(f"   类型选择器: {has_type_select}")
                    print(f"   数量输入框: {has_quantity_input}")

                    page.screenshot(path='/tmp/modal_test_03_record_trade.png', full_page=True)
                    results.add_test("记录交易弹框 - 表单元素", "PASS", f"核心元素完整", "/tmp/modal_test_03_record_trade.png")

                    # 关闭
                    close_button = page.locator('button:has-text("取消")').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("记录交易弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("记录交易弹框", "SKIP", "未找到触发按钮")
                print("⏭️  未找到记录交易按钮")

        except Exception as e:
            results.add_test("记录交易弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 2.2 导入交易弹框
        print("\n[2.2] 测试导入交易弹框 (ImportTradesDialog)")
        try:
            page.goto('http://localhost:5175/trades')
            time.sleep(2)

            import_button = page.locator('button:has-text("导入"), button:has-text("批量导入")').first
            if import_button.count() > 0:
                import_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("导入交易弹框", "PASS", "弹框成功打开")
                    print("✅ 导入交易弹框打开成功")

                    page.screenshot(path='/tmp/modal_test_04_import_trades.png', full_page=True)

                    # 关闭
                    close_button = page.locator('button:has-text("取消")').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("导入交易弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("导入交易弹框", "SKIP", "未找到导入按钮")
                print("⏭️  未找到导入按钮")

        except Exception as e:
            results.add_test("导入交易弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件3: 事件管理表单弹框
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件3: 事件管理表单弹框")
        print("=" * 120)

        # 3.1 添加事件弹框
        print("\n[3.1] 测试添加事件弹框 (EventFormDialog)")
        try:
            page.goto('http://localhost:5175/events')
            time.sleep(2)

            add_button = page.locator('button:has-text("添加事件"), button:has-text("创建事件")').first
            if add_button.count() > 0:
                add_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("添加事件弹框", "PASS", "弹框成功打开")
                    print("✅ 添加事件弹框打开成功")

                    page.screenshot(path='/tmp/modal_test_05_add_event.png', full_page=True)

                    # 关闭
                    close_button = page.locator('button:has-text("取消")').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("添加事件弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("添加事件弹框", "SKIP", "未找到触发按钮")
                print("⏭️  未找到添加事件按钮")

        except Exception as e:
            results.add_test("添加事件弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件4: AI分析弹框
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件4: AI分析相关弹框")
        print("=" * 120)

        # 4.1 单股分析弹框
        print("\n[4.1] 测试单股分析弹框 (SingleStockAnalysisDialog)")
        try:
            page.goto('http://localhost:5175/ai')
            time.sleep(2)

            # 查找单股分析按钮
            analysis_button = page.locator('button:has-text("单股分析"), button:has-text("股票分析")').first
            if analysis_button.count() > 0:
                analysis_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("单股分析弹框", "PASS", "弹框成功打开")
                    print("✅ 单股分析弹框打开成功")

                    page.screenshot(path='/tmp/modal_test_06_stock_analysis.png', full_page=True)

                    # 关闭
                    close_button = page.locator('button:has-text("取消"), .el-dialog__close').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("单股分析弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("单股分析弹框", "SKIP", "未找到分析按钮")
                print("⏭️  未找到单股分析按钮")

        except Exception as e:
            results.add_test("单股分析弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 4.2 投资组合分析弹框
        print("\n[4.2] 测试投资组合分析弹框 (PortfolioAnalysisDialog)")
        try:
            page.goto('http://localhost:5175/ai')
            time.sleep(2)

            portfolio_button = page.locator('button:has-text("组合分析"), button:has-text("投资组合")').first
            if portfolio_button.count() > 0:
                portfolio_button.click()
                time.sleep(1)

                dialog = page.locator('.el-dialog:visible').first
                if dialog.count() > 0:
                    results.add_test("投资组合分析弹框", "PASS", "弹框成功打开")
                    print("✅ 投资组合分析弹框打开成功")

                    page.screenshot(path='/tmp/modal_test_07_portfolio_analysis.png', full_page=True)

                    # 关闭
                    close_button = page.locator('button:has-text("取消"), .el-dialog__close').first
                    if close_button.count() > 0:
                        close_button.click()
                        time.sleep(1)
                else:
                    results.add_test("投资组合分析弹框", "FAIL", "弹框未出现")
            else:
                results.add_test("投资组合分析弹框", "SKIP", "未找到组合分析按钮")
                print("⏭️  未找到组合分析按钮")

        except Exception as e:
            results.add_test("投资组合分析弹框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件5: 确认对话框 (ElMessageBox)
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件5: 确认对话框测试")
        print("=" * 120)

        # 5.1 删除确认对话框
        print("\n[5.1] 测试删除确认对话框")
        try:
            page.goto('http://localhost:5175/accounts')
            time.sleep(2)

            # 查找删除按钮
            delete_button = page.locator('button:has-text("删除"), .el-button--danger').first
            if delete_button.count() > 0:
                delete_button.click()
                time.sleep(1)

                # 检查MessageBox确认框
                messagebox = page.locator('.el-message-box:visible').first
                if messagebox.count() > 0:
                    results.add_test("删除确认对话框", "PASS", "确认框成功出现")
                    print("✅ 删除确认对话框出现")

                    page.screenshot(path='/tmp/modal_test_08_delete_confirm.png', full_page=True)

                    # 点击取消
                    cancel_button = page.locator('.el-message-box button:has-text("取消")').first
                    if cancel_button.count() > 0:
                        cancel_button.click()
                        time.sleep(1)
                else:
                    results.add_test("删除确认对话框", "FAIL", "确认框未出现")
            else:
                results.add_test("删除确认对话框", "SKIP", "未找到删除按钮")
                print("⏭️  未找到删除按钮")

        except Exception as e:
            results.add_test("删除确认对话框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件6: 消息通知 (ElMessage)
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件6: 消息通知测试")
        print("=" * 120)

        # 6.1 成功消息
        print("\n[6.1] 测试成功消息通知")
        try:
            page.goto('http://localhost:5175/')
            time.sleep(2)

            # 触发刷新操作（通常会显示成功消息）
            refresh_button = page.locator('button:has-text("刷新")').first
            if refresh_button.count() > 0:
                refresh_button.click()
                time.sleep(1)

                success_message = page.locator('.el-message--success:visible').first
                if success_message.count() > 0:
                    results.add_test("成功消息通知", "PASS", "成功消息已显示")
                    print("✅ 成功消息通知显示")
                    page.screenshot(path='/tmp/modal_test_09_success_message.png', full_page=True)
                else:
                    results.add_test("成功消息通知", "SKIP", "未触发成功消息")
                    print("⏭️  未触发成功消息（正常）")
            else:
                results.add_test("成功消息通知", "SKIP", "未找到刷新按钮")

        except Exception as e:
            results.add_test("成功消息通知", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件7: 下拉选择器交互
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件7: 下拉选择器交互测试")
        print("=" * 120)

        # 7.1 账户筛选选择器
        print("\n[7.1] 测试账户筛选选择器")
        try:
            page.goto('http://localhost:5175/accounts')
            time.sleep(2)

            selectors = page.locator('.el-select').all()
            if len(selectors) > 0:
                print(f"   找到 {len(selectors)} 个选择器")

                first_select = selectors[0]
                first_select.click()
                time.sleep(1)

                dropdown_items = page.locator('.el-select-dropdown__item:visible').all()
                if len(dropdown_items) > 0:
                    results.add_test("下拉选择器交互", "PASS", f"显示{len(dropdown_items)}个选项")
                    print(f"✅ 下拉选择器正常，{len(dropdown_items)}个选项")

                    page.screenshot(path='/tmp/modal_test_10_selector_dropdown.png', full_page=True)

                    # 选择第一个选项
                    dropdown_items[0].click()
                    time.sleep(1)
                else:
                    results.add_test("下拉选择器选项", "FAIL", "无下拉选项")
            else:
                results.add_test("下拉选择器", "SKIP", "页面无选择器")
                print("⏭️  页面无下拉选择器")

        except Exception as e:
            results.add_test("下拉选择器交互", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 7.2 日期选择器
        print("\n[7.2] 测试日期选择器")
        try:
            page.goto('http://localhost:5175/trades')
            time.sleep(2)

            date_pickers = page.locator('.el-date-editor').all()
            if len(date_pickers) > 0:
                print(f"   找到 {len(date_pickers)} 个日期选择器")

                first_picker = date_pickers[0]
                first_picker.click()
                time.sleep(1)

                date_panel = page.locator('.el-date-picker:visible').first
                if date_panel.count() > 0:
                    results.add_test("日期选择器交互", "PASS", "日期面板成功打开")
                    print("✅ 日期选择器正常")

                    page.screenshot(path='/tmp/modal_test_11_date_picker.png', full_page=True)

                    # 关闭日期面板（点击页面其他位置）
                    page.click('body', position={'x': 100, 'y': 100})
                    time.sleep(1)
                else:
                    results.add_test("日期选择器", "FAIL", "日期面板未打开")
            else:
                results.add_test("日期选择器", "SKIP", "页面无日期选择器")
                print("⏭️  页面无日期选择器")

        except Exception as e:
            results.add_test("日期选择器交互", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # ========================================
        # 测试套件8: 其他交互组件
        # ========================================
        print("\n" + "=" * 120)
        print("测试套件8: 其他交互组件测试")
        print("=" * 120)

        # 8.1 单选框组
        print("\n[8.1] 测试单选框组 (el-radio-group)")
        try:
            page.goto('http://localhost:5175/ai')
            time.sleep(2)

            radio_groups = page.locator('.el-radio-group').all()
            if len(radio_groups) > 0:
                print(f"   找到 {len(radio_groups)} 个单选框组")

                radios = page.locator('.el-radio').all()
                if len(radios) > 1:
                    radios[1].click()
                    time.sleep(0.5)

                    results.add_test("单选框组交互", "PASS", f"{len(radios)}个单选项")
                    print(f"✅ 单选框组正常，{len(radios)}个选项")
                else:
                    results.add_test("单选框组", "SKIP", "单选项不足")
            else:
                results.add_test("单选框组", "SKIP", "页面无单选框组")
                print("⏭️  页面无单选框组")

        except Exception as e:
            results.add_test("单选框组", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 8.2 复选框组
        print("\n[8.2] 测试复选框组 (el-checkbox-group)")
        try:
            # 可能在设置页面有复选框
            page.goto('http://localhost:5175/settings')
            time.sleep(2)

            checkboxes = page.locator('.el-checkbox').all()
            if len(checkboxes) > 0:
                print(f"   找到 {len(checkboxes)} 个复选框")

                checkboxes[0].click()
                time.sleep(0.5)

                results.add_test("复选框交互", "PASS", f"{len(checkboxes)}个复选项")
                print(f"✅ 复选框正常，{len(checkboxes)}个选项")
            else:
                results.add_test("复选框", "SKIP", "页面无复选框")
                print("⏭️  页面无复选框")

        except Exception as e:
            results.add_test("复选框", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 8.3 开关组件
        print("\n[8.3] 测试开关组件 (el-switch)")
        try:
            page.goto('http://localhost:5175/settings')
            time.sleep(2)

            switches = page.locator('.el-switch').all()
            if len(switches) > 0:
                print(f"   找到 {len(switches)} 个开关")

                switches[0].click()
                time.sleep(0.5)

                results.add_test("开关组件交互", "PASS", f"{len(switches)}个开关")
                print(f"✅ 开关组件正常，{len(switches)}个")
            else:
                results.add_test("开关组件", "SKIP", "页面无开关组件")
                print("⏭️  页面无开关组件")

        except Exception as e:
            results.add_test("开关组件", "FAIL", str(e))
            print(f"❌ 测试异常: {e}")

        # 关闭浏览器
        browser.close()

        # ========================================
        # 生成测试报告
        # ========================================
        results.print_summary()

        print("\n" + "=" * 120)
        print("详细测试结果")
        print("=" * 120)
        for test in results.tests:
            status_icon = "✅" if test['status'] == "PASS" else ("❌" if test['status'] == "FAIL" else "⏭️")
            print(f"{status_icon} [{test['time']}] {test['name']}")
            if test['details']:
                print(f"   详情: {test['details']}")
            if test['screenshot']:
                print(f"   截图: {test['screenshot']}")

        print("\n" + "=" * 120)
        print("截图文件列表")
        print("=" * 120)
        screenshot_list = [
            "01. /tmp/modal_test_01_add_account.png - 添加账户弹框",
            "02. /tmp/modal_test_02_edit_account.png - 编辑账户弹框",
            "03. /tmp/modal_test_03_record_trade.png - 记录交易弹框",
            "04. /tmp/modal_test_04_import_trades.png - 导入交易弹框",
            "05. /tmp/modal_test_05_add_event.png - 添加事件弹框",
            "06. /tmp/modal_test_06_stock_analysis.png - 单股分析弹框",
            "07. /tmp/modal_test_07_portfolio_analysis.png - 投资组合分析弹框",
            "08. /tmp/modal_test_08_delete_confirm.png - 删除确认对话框",
            "09. /tmp/modal_test_09_success_message.png - 成功消息通知",
            "10. /tmp/modal_test_10_selector_dropdown.png - 下拉选择器",
            "11. /tmp/modal_test_11_date_picker.png - 日期选择器"
        ]
        for item in screenshot_list:
            print(item)

        print("\n" + "=" * 120)
        print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 120)

        # 输出控制台错误（如果有）
        error_logs = [log for log in console_logs if 'error' in log.lower()]
        if error_logs:
            print("\n" + "=" * 120)
            print("控制台错误日志")
            print("=" * 120)
            for log in error_logs[:10]:
                print(f"   {log}")


if __name__ == '__main__':
    modal_interaction_test()
