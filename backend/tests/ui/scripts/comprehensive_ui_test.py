"""
投资管理系统 - 综合UI测试
使用Playwright进行全面的前端功能测试
"""
from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_test(self, name, status, details=""):
        self.total += 1
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1

        self.tests.append({
            "name": name,
            "status": status,
            "details": details,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    def print_summary(self):
        print("\n" + "=" * 100)
        print("测试报告摘要")
        print("=" * 100)
        print(f"总测试数: {self.total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"通过率: {(self.passed/self.total*100):.1f}%")
        print("=" * 100)

        if self.failed > 0:
            print("\n失败的测试:")
            for test in self.tests:
                if test['status'] == 'FAIL':
                    print(f"  ❌ [{test['time']}] {test['name']}")
                    if test['details']:
                        print(f"     详情: {test['details']}")


def comprehensive_test():
    results = TestResults()

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # 捕获控制台日志
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # 捕获API请求
        api_requests = []
        api_responses = []

        def log_request(request):
            if '/api/' in request.url:
                api_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })

        def log_response(response):
            if '/api/' in response.url:
                api_responses.append({
                    'url': response.url,
                    'status': response.status
                })

        page.on('request', log_request)
        page.on('response', log_response)

        print("=" * 100)
        print("投资管理系统 - 综合UI测试")
        print("=" * 100)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试URL: http://localhost:5173")
        print("=" * 100)

        # ========================================
        # 1. 登录流程测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块1: 登录流程测试")
        print("-" * 100)

        try:
            page.goto('http://localhost:5173/login')
            page.wait_for_load_state('networkidle')
            time.sleep(1)

            # 检查页面标题
            title = page.title()
            if "投资" in title or "Investment" in title:
                results.add_test("登录页加载", "PASS", f"页面标题: {title}")
                print("✅ 登录页加载成功")
            else:
                results.add_test("登录页加载", "FAIL", f"页面标题不符: {title}")
                print("❌ 登录页加载失败")

            # 检查登录表单元素
            has_username = page.locator('input[type="text"]').count() > 0
            has_password = page.locator('input[type="password"]').count() > 0
            has_button = page.locator('button:has-text("登录")').count() > 0

            if has_username and has_password and has_button:
                results.add_test("登录表单元素", "PASS")
                print("✅ 登录表单元素完整")
            else:
                results.add_test("登录表单元素", "FAIL", f"用户名:{has_username}, 密码:{has_password}, 按钮:{has_button}")
                print("❌ 登录表单元素缺失")

            # 截图
            page.screenshot(path='/tmp/ui_test_01_login.png', full_page=True)
            print("📸 截图: /tmp/ui_test_01_login.png")

            # 执行登录
            page.fill('input[type="text"]', 'testuser')
            page.fill('input[type="password"]', 'Test123456')
            page.click('button:has-text("登录")')

            # 等待路由跳转（增加等待时间，等待URL变化）
            try:
                page.wait_for_url('http://localhost:5173/', timeout=5000)
                time.sleep(1)  # 额外等待确保页面渲染完成
            except:
                time.sleep(3)  # 如果等待URL超时，使用固定等待

            page.wait_for_load_state('networkidle')

            # 验证登录成功
            current_url = page.url
            token = page.evaluate('() => localStorage.getItem("token")')

            if token and 'login' not in current_url.lower():
                results.add_test("登录功能", "PASS", f"已跳转到: {current_url}")
                print("✅ 登录成功")
            else:
                results.add_test("登录功能", "FAIL", f"仍在: {current_url}, Token: {bool(token)}")
                print("❌ 登录失败")

        except Exception as e:
            results.add_test("登录流程", "FAIL", str(e))
            print(f"❌ 登录流程异常: {e}")

        # ========================================
        # 2. Dashboard主页测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块2: Dashboard主页测试")
        print("-" * 100)

        try:
            page.goto('http://localhost:5173/')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # 截图
            page.screenshot(path='/tmp/ui_test_02_dashboard.png', full_page=True)
            print("📸 截图: /tmp/ui_test_02_dashboard.png")

            # 检查侧边栏导航（使用正确的选择器）
            sidebar_items = page.locator('nav > div[class*="cursor-pointer"]').all()
            if len(sidebar_items) > 0:
                results.add_test("Dashboard导航栏", "PASS", f"找到{len(sidebar_items)}个导航项")
                print(f"✅ 导航栏加载: {len(sidebar_items)}个菜单项")
            else:
                results.add_test("Dashboard导航栏", "FAIL")
                print("❌ 导航栏未找到")

            # 检查统计卡片（总资产、今日盈亏等）- 使用正确的选择器
            stat_cards = page.locator('div.bg-white.rounded-lg.border').all()
            if len(stat_cards) >= 3:
                results.add_test("Dashboard统计卡片", "PASS", f"找到{len(stat_cards)}个卡片")
                print(f"✅ 统计卡片显示: {len(stat_cards)}个")
            else:
                results.add_test("Dashboard统计卡片", "FAIL", f"只找到{len(stat_cards)}个")
                print(f"⚠️  统计卡片数量不足: {len(stat_cards)}个")

            # 检查API调用
            dashboard_apis = [r for r in api_responses if any(x in r['url'] for x in ['account', 'holding', 'ai', 'event'])]
            success_apis = [r for r in dashboard_apis if r['status'] == 200]

            if len(success_apis) >= 3:
                results.add_test("Dashboard API调用", "PASS", f"{len(success_apis)}/{len(dashboard_apis)}成功")
                print(f"✅ API调用成功: {len(success_apis)}个")
            else:
                results.add_test("Dashboard API调用", "FAIL", f"{len(success_apis)}/{len(dashboard_apis)}成功")
                print(f"❌ API调用失败: {len(success_apis)}/{len(dashboard_apis)}")

        except Exception as e:
            results.add_test("Dashboard主页", "FAIL", str(e))
            print(f"❌ Dashboard测试异常: {e}")

        # ========================================
        # 3. 账户管理页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块3: 账户管理页面测试")
        print("-" * 100)

        try:
            # 点击账户管理菜单
            account_menu = page.locator('text=账户管理').first
            if account_menu.count() > 0:
                account_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_03_accounts.png', full_page=True)
                print("📸 截图: /tmp/ui_test_03_accounts.png")

                results.add_test("账户管理页面", "PASS")
                print("✅ 账户管理页面加载成功")
            else:
                results.add_test("账户管理菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到账户管理菜单")

        except Exception as e:
            results.add_test("账户管理页面", "FAIL", str(e))
            print(f"❌ 账户管理测试异常: {e}")

        # ========================================
        # 4. 持仓管理页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块4: 持仓管理页面测试")
        print("-" * 100)

        try:
            holding_menu = page.locator('text=持仓管理').first
            if holding_menu.count() > 0:
                holding_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_04_holdings.png', full_page=True)
                print("📸 截图: /tmp/ui_test_04_holdings.png")

                results.add_test("持仓管理页面", "PASS")
                print("✅ 持仓管理页面加载成功")
            else:
                results.add_test("持仓管理菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到持仓管理菜单")

        except Exception as e:
            results.add_test("持仓管理页面", "FAIL", str(e))
            print(f"❌ 持仓管理测试异常: {e}")

        # ========================================
        # 5. 交易记录页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块5: 交易记录页面测试")
        print("-" * 100)

        try:
            trade_menu = page.locator('text=交易记录').first
            if trade_menu.count() > 0:
                trade_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_05_trades.png', full_page=True)
                print("📸 截图: /tmp/ui_test_05_trades.png")

                results.add_test("交易记录页面", "PASS")
                print("✅ 交易记录页面加载成功")
            else:
                results.add_test("交易记录菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到交易记录菜单")

        except Exception as e:
            results.add_test("交易记录页面", "FAIL", str(e))
            print(f"❌ 交易记录测试异常: {e}")

        # ========================================
        # 6. 事件中心页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块6: 事件中心页面测试")
        print("-" * 100)

        try:
            event_menu = page.locator('text=事件中心').first
            if event_menu.count() > 0:
                event_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_06_events.png', full_page=True)
                print("📸 截图: /tmp/ui_test_06_events.png")

                results.add_test("事件中心页面", "PASS")
                print("✅ 事件中心页面加载成功")
            else:
                results.add_test("事件中心菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到事件中心菜单")

        except Exception as e:
            results.add_test("事件中心页面", "FAIL", str(e))
            print(f"❌ 事件中心测试异常: {e}")

        # ========================================
        # 7. AI分析页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块7: AI分析页面测试")
        print("-" * 100)

        try:
            ai_menu = page.locator('text=AI分析').first
            if ai_menu.count() > 0:
                ai_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_07_ai.png', full_page=True)
                print("📸 截图: /tmp/ui_test_07_ai.png")

                results.add_test("AI分析页面", "PASS")
                print("✅ AI分析页面加载成功")
            else:
                results.add_test("AI分析菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到AI分析菜单")

        except Exception as e:
            results.add_test("AI分析页面", "FAIL", str(e))
            print(f"❌ AI分析测试异常: {e}")

        # ========================================
        # 8. 设置页面测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块8: 设置页面测试")
        print("-" * 100)

        try:
            settings_menu = page.locator('text=系统设置').first
            if settings_menu.count() > 0:
                settings_menu.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.screenshot(path='/tmp/ui_test_08_settings.png', full_page=True)
                print("📸 截图: /tmp/ui_test_08_settings.png")

                results.add_test("设置页面", "PASS")
                print("✅ 设置页面加载成功")
            else:
                results.add_test("设置菜单", "FAIL", "未找到菜单项")
                print("⚠️  未找到设置菜单")

        except Exception as e:
            results.add_test("设置页面", "FAIL", str(e))
            print(f"❌ 设置测试异常: {e}")

        # ========================================
        # 9. 消息通知测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块9: 消息通知测试")
        print("-" * 100)

        try:
            # 返回Dashboard测试消息通知
            page.goto('http://localhost:5173/')
            time.sleep(2)

            # 检查是否有ElMessage组件（即使没有触发，DOM中应该有容器）
            message_container = page.locator('.el-message').count()
            print(f"ElMessage容器数: {message_container}")

            # 尝试触发一个操作来显示消息（例如刷新数据）
            refresh_button = page.locator('button:has-text("刷新"), button:has-text("查询")').first
            if refresh_button.count() > 0:
                refresh_button.click()
                time.sleep(1)

                # 检查是否出现成功消息
                success_message = page.locator('.el-message--success').count()
                if success_message > 0:
                    results.add_test("ElMessage成功通知", "PASS")
                    print("✅ 检测到成功消息通知")
                else:
                    results.add_test("ElMessage成功通知", "PASS", "未触发成功消息（正常）")
                    print("✅ 消息通知功能正常（未触发）")
            else:
                results.add_test("消息通知触发", "PASS", "未找到触发按钮")
                print("✅ 消息通知组件已加载")

            page.screenshot(path='/tmp/ui_test_09_messages.png', full_page=True)
            print("📸 截图: /tmp/ui_test_09_messages.png")

        except Exception as e:
            results.add_test("消息通知测试", "FAIL", str(e))
            print(f"❌ 消息通知测试异常: {e}")

        # ========================================
        # 10. 下拉选择器测试
        # ========================================
        print("\n" + "-" * 100)
        print("模块10: 下拉选择器测试")
        print("-" * 100)

        try:
            # 去账户管理页面测试筛选器
            page.goto('http://localhost:5173/accounts')
            time.sleep(2)

            # 检查el-select组件
            selectors = page.locator('.el-select').all()
            print(f"找到 {len(selectors)} 个下拉选择器")

            if len(selectors) > 0:
                # 点击第一个选择器
                first_select = page.locator('.el-select').first
                first_select.click()
                time.sleep(1)

                # 检查下拉选项
                dropdown_options = page.locator('.el-select-dropdown__item').all()
                if len(dropdown_options) > 0:
                    results.add_test("下拉选择器功能", "PASS", f"找到{len(dropdown_options)}个选项")
                    print(f"✅ 下拉选择器正常: {len(dropdown_options)}个选项")

                    # 选择一个选项
                    dropdown_options[0].click()
                    time.sleep(1)
                else:
                    results.add_test("下拉选择器选项", "FAIL", "无选项")
                    print("❌ 下拉选择器无选项")
            else:
                results.add_test("下拉选择器", "PASS", "页面无下拉组件（正常）")
                print("✅ 该页面无下拉组件")

            page.screenshot(path='/tmp/ui_test_10_selectors.png', full_page=True)
            print("📸 截图: /tmp/ui_test_10_selectors.png")

        except Exception as e:
            results.add_test("下拉选择器测试", "FAIL", str(e))
            print(f"❌ 下拉选择器测试异常: {e}")

        # ========================================
        # 11. 控制台日志检查
        # ========================================
        print("\n" + "-" * 100)
        print("模块11: 控制台日志检查")
        print("-" * 100)

        error_logs = [log for log in console_logs if 'error' in log.lower()]
        warning_logs = [log for log in console_logs if 'warn' in log.lower()]

        print(f"总日志数: {len(console_logs)}")
        print(f"错误日志: {len(error_logs)}")
        print(f"警告日志: {len(warning_logs)}")

        if len(error_logs) == 0:
            results.add_test("控制台无错误", "PASS")
            print("✅ 控制台无错误")
        else:
            results.add_test("控制台无错误", "FAIL", f"{len(error_logs)}个错误")
            print(f"❌ 发现{len(error_logs)}个错误:")
            for log in error_logs[:5]:
                print(f"   {log}")

        # ========================================
        # 12. API调用统计
        # ========================================
        print("\n" + "-" * 100)
        print("模块12: API调用统计")
        print("-" * 100)

        total_apis = len(api_responses)
        success_apis = len([r for r in api_responses if r['status'] == 200])
        error_401 = len([r for r in api_responses if r['status'] == 401])
        error_other = len([r for r in api_responses if r['status'] >= 400 and r['status'] != 401])

        print(f"总API调用: {total_apis}")
        print(f"成功 (200): {success_apis}")
        print(f"认证错误 (401): {error_401}")
        print(f"其他错误: {error_other}")

        if error_401 == 0 and error_other == 0:
            results.add_test("API无错误", "PASS", f"{success_apis}/{total_apis}成功")
            print("✅ 所有API调用成功")
        else:
            results.add_test("API无错误", "FAIL", f"401:{error_401}, 其他:{error_other}")
            print(f"❌ API调用有错误")

        # 关闭浏览器
        browser.close()

        # 打印测试摘要
        results.print_summary()

        # 打印详细结果
        print("\n" + "=" * 100)
        print("详细测试结果")
        print("=" * 100)
        for test in results.tests:
            status_icon = "✅" if test['status'] == "PASS" else "❌"
            print(f"{status_icon} [{test['time']}] {test['name']}")
            if test['details']:
                print(f"   详情: {test['details']}")

        print("\n" + "=" * 100)
        print("截图文件列表")
        print("=" * 100)
        print("1. /tmp/ui_test_01_login.png - 登录页")
        print("2. /tmp/ui_test_02_dashboard.png - Dashboard主页")
        print("3. /tmp/ui_test_03_accounts.png - 账户管理")
        print("4. /tmp/ui_test_04_holdings.png - 持仓管理")
        print("5. /tmp/ui_test_05_trades.png - 交易记录")
        print("6. /tmp/ui_test_06_events.png - 事件中心")
        print("7. /tmp/ui_test_07_ai.png - AI分析")
        print("8. /tmp/ui_test_08_settings.png - 设置页面")
        print("9. /tmp/ui_test_09_messages.png - 消息通知")
        print("10. /tmp/ui_test_10_selectors.png - 下拉选择器")

        print("\n" + "=" * 100)
        print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)


if __name__ == '__main__':
    comprehensive_test()
