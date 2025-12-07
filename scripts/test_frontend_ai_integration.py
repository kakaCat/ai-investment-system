#!/usr/bin/env python3
"""
前端AI集成自动化测试脚本
测试所有AI API端点的功能性
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime


class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


class AIIntegrationTester:
    """AI集成测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.access_token = None
        self.test_username = f"testuser_{int(time.time())}"
        self.test_password = "testpass123"

    def log(self, message: str, level: str = "INFO"):
        """彩色日志输出"""
        color = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "ERROR": Colors.RED,
            "WARNING": Colors.YELLOW
        }.get(level, Colors.END)

        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")

    def register_and_login(self) -> bool:
        """注册并登录测试用户"""
        self.log("注册测试用户...", "INFO")
        try:
            # 注册
            register_response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={
                    "username": self.test_username,
                    "password": self.test_password,
                    "nickname": "测试用户"
                },
                timeout=10
            )

            if register_response.status_code not in [200, 201]:
                # 可能用户已存在，尝试直接登录
                self.log("⚠️  注册失败，尝试直接登录...", "WARNING")
            else:
                self.log(f"✅ 用户注册成功: {self.test_username}", "SUCCESS")

            # 登录 (OAuth2PasswordRequestForm需要form-data格式)
            self.log("登录获取Token...", "INFO")
            login_response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={  # 注意：使用data而不是json
                    "username": self.test_username,
                    "password": self.test_password
                },
                timeout=10
            )

            if login_response.status_code != 200:
                self.log(f"❌ 登录失败: {login_response.status_code} - {login_response.text}", "ERROR")
                return False

            token_data = login_response.json()
            self.access_token = token_data.get("access_token")

            if not self.access_token:
                self.log("❌ 未获取到access_token", "ERROR")
                return False

            self.log(f"✅ 登录成功，Token: {self.access_token[:20]}...", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"❌ 认证失败: {e}", "ERROR")
            return False

    def get_headers(self) -> dict:
        """获取认证头"""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    def test_health(self) -> bool:
        """测试后端健康状态"""
        self.log("测试后端健康状态...", "INFO")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log("✅ 后端健康状态正常", "SUCCESS")
                    return True
            self.log("❌ 后端健康检查失败", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ 后端连接失败: {e}", "ERROR")
            return False

    def test_single_analysis(self) -> Dict[str, Any]:
        """TC-001: 测试单股AI分析"""
        self.log("\n" + "="*60, "INFO")
        self.log("TC-001: 单股AI分析完整流程测试", "INFO")
        self.log("="*60, "INFO")

        result = {
            "test_case": "TC-001",
            "name": "单股AI分析",
            "status": "PENDING",
            "details": [],
            "errors": []
        }

        # 准备测试数据
        request_data = {
            "symbol": "600519",
            "stock_name": "贵州茅台",
            "dimensions": ["fundamentals", "technicals"],
            "include_fundamentals": True,
            "include_technicals": True
        }

        self.log(f"📊 测试股票: {request_data['stock_name']} ({request_data['symbol']})", "INFO")
        self.log(f"📊 分析维度: {', '.join(request_data['dimensions'])}", "INFO")

        try:
            # 发送请求
            self.log("🚀 发送AI分析请求...", "INFO")
            start_time = time.time()

            response = requests.post(
                f"{self.base_url}/api/v1/ai/single-analysis",
                json=request_data,
                headers=self.get_headers(),
                timeout=120  # 2分钟超时
            )

            elapsed_time = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed_time:.2f}秒", "INFO")

            # 检查响应状态码
            if response.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"HTTP {response.status_code}: {response.text}")
                self.log(f"❌ API返回错误: {response.status_code}", "ERROR")
                self.log(f"错误详情: {response.text}", "ERROR")
                return result

            # 解析响应数据
            data = response.json()

            # 验证响应结构
            if "data" not in data:
                result["status"] = "FAILED"
                result["errors"].append("响应缺少data字段")
                self.log("❌ 响应格式错误：缺少data字段", "ERROR")
                return result

            analysis = data["data"]

            # 验证必需字段
            required_fields = [
                "symbol", "stock_name", "ai_score", "ai_suggestion",
                "confidence_level", "dimensions_analyzed", "created_at"
            ]

            missing_fields = [field for field in required_fields if field not in analysis]
            if missing_fields:
                result["status"] = "FAILED"
                result["errors"].append(f"缺少字段: {missing_fields}")
                self.log(f"❌ 响应缺少字段: {missing_fields}", "ERROR")
                return result

            # 验证AI评分
            ai_score = analysis["ai_score"]
            overall_score = ai_score.get("overall_score", 0)

            self.log("\n📈 AI分析结果:", "INFO")
            self.log(f"   股票: {analysis['stock_name']} ({analysis['symbol']})", "INFO")
            self.log(f"   综合评分: {overall_score}/100", "SUCCESS" if overall_score > 0 else "ERROR")

            # 验证评分范围
            if not (0 <= overall_score <= 100):
                result["errors"].append(f"评分超出范围: {overall_score}")
                self.log(f"⚠️  警告: 评分超出0-100范围: {overall_score}", "WARNING")

            # 显示分维度评分
            if "fundamental_score" in ai_score:
                self.log(f"   基本面评分: {ai_score['fundamental_score']}/100", "INFO")
            if "technical_score" in ai_score:
                self.log(f"   技术面评分: {ai_score['technical_score']}/100", "INFO")
            if "valuation_score" in ai_score:
                self.log(f"   估值评分: {ai_score['valuation_score']}/100", "INFO")

            # 显示置信度
            confidence = analysis["confidence_level"]
            confidence_label = "高" if confidence >= 70 else "中" if confidence >= 50 else "低"
            self.log(f"   置信度: {confidence}% ({confidence_label})", "INFO")

            # 显示AI建议（前200字符）
            suggestion = analysis["ai_suggestion"]
            suggestion_preview = suggestion[:200] + "..." if len(suggestion) > 200 else suggestion
            self.log(f"\n💡 AI投资建议:", "INFO")
            self.log(f"   {suggestion_preview}", "INFO")

            # 显示数据来源
            if "data_source" in analysis:
                source_map = {
                    "tushare": "Tushare专业数据",
                    "akshare": "AkShare数据",
                    "mock": "Mock数据"
                }
                source_label = source_map.get(analysis["data_source"], analysis["data_source"])
                self.log(f"   数据来源: {source_label}", "INFO")

            # 显示分析维度
            self.log(f"   分析维度: {', '.join(analysis['dimensions_analyzed'])}", "INFO")

            # 记录成功
            result["status"] = "PASSED"
            result["details"].append({
                "overall_score": overall_score,
                "confidence_level": confidence,
                "response_time": elapsed_time,
                "data_source": analysis.get("data_source", "unknown")
            })

            self.log("\n✅ TC-001 测试通过", "SUCCESS")

        except requests.Timeout:
            result["status"] = "FAILED"
            result["errors"].append("请求超时（>120秒）")
            self.log("❌ 请求超时", "ERROR")
        except Exception as e:
            result["status"] = "FAILED"
            result["errors"].append(str(e))
            self.log(f"❌ 测试异常: {e}", "ERROR")

        self.test_results.append(result)
        return result

    def test_chat(self) -> Dict[str, Any]:
        """TC-002: 测试AI对话"""
        self.log("\n" + "="*60, "INFO")
        self.log("TC-002: AI投资对话多轮对话测试", "INFO")
        self.log("="*60, "INFO")

        result = {
            "test_case": "TC-002",
            "name": "AI投资对话",
            "status": "PENDING",
            "details": [],
            "errors": []
        }

        try:
            # 第一轮对话
            self.log("💬 测试对话1: 什么是价值投资？", "INFO")
            start_time = time.time()

            request1 = {
                "message": "什么是价值投资？",
                "context": []
            }

            response1 = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=request1,
                headers=self.get_headers(),
                timeout=60
            )

            elapsed1 = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed1:.2f}秒", "INFO")

            if response1.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"对话1失败: HTTP {response1.status_code}")
                self.log(f"❌ 对话1失败: {response1.status_code}", "ERROR")
                self.test_results.append(result)
                return result

            data1 = response1.json()
            reply1 = data1["data"]["reply"]
            self.log(f"🤖 AI回复1: {reply1[:100]}...", "INFO")

            # 第二轮对话（带上下文）
            self.log("\n💬 测试对话2 (带上下文): 如何应用到A股市场？", "INFO")
            start_time = time.time()

            request2 = {
                "message": "如何应用到A股市场？",
                "context": [
                    {"role": "user", "content": "什么是价值投资？"},
                    {"role": "assistant", "content": reply1}
                ]
            }

            response2 = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=request2,
                headers=self.get_headers(),
                timeout=60
            )

            elapsed2 = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed2:.2f}秒", "INFO")

            if response2.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"对话2失败: HTTP {response2.status_code}")
                self.log(f"❌ 对话2失败: {response2.status_code}", "ERROR")
                self.test_results.append(result)
                return result

            data2 = response2.json()
            reply2 = data2["data"]["reply"]
            self.log(f"🤖 AI回复2: {reply2[:100]}...", "INFO")

            # 记录成功
            result["status"] = "PASSED"
            result["details"].append({
                "rounds": 2,
                "avg_response_time": (elapsed1 + elapsed2) / 2
            })

            self.log("\n✅ TC-002 测试通过", "SUCCESS")

        except requests.Timeout:
            result["status"] = "FAILED"
            result["errors"].append("请求超时")
            self.log("❌ 请求超时", "ERROR")
        except Exception as e:
            result["status"] = "FAILED"
            result["errors"].append(str(e))
            self.log(f"❌ 测试异常: {e}", "ERROR")

        self.test_results.append(result)
        return result

    def test_chat_old(self) -> Dict[str, Any]:
        """TC-002: 测试AI对话（旧版，已弃用）"""
        self.log("\n" + "="*60, "INFO")
        self.log("TC-002: AI投资对话多轮对话测试", "INFO")
        self.log("="*60, "INFO")

        result = {
            "test_case": "TC-002",
            "name": "AI投资对话",
            "status": "PENDING",
            "details": [],
            "errors": []
        }

        try:
            # 第一轮对话（无上下文）
            self.log("💬 测试对话1: 什么是价值投资？", "INFO")
            start_time = time.time()

            request1 = {
                "message": "什么是价值投资？",
                "context": []
            }

            response1 = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=request1,
                headers=self.get_headers(),
                timeout=60
            )

            elapsed1 = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed1:.2f}秒", "INFO")

            if response1.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"对话1失败: HTTP {response1.status_code}")
                self.log(f"❌ 对话1失败: {response1.status_code}", "ERROR")
                return result

            data1 = response1.json()
            reply1 = data1["data"]["reply"]

            self.log(f"🤖 AI回复1: {reply1[:150]}...", "INFO")

            # 第二轮对话（带上下文）
            self.log("\n💬 测试对话2 (带上下文): 如何应用到A股市场？", "INFO")
            start_time = time.time()

            request2 = {
                "message": "如何应用到A股市场？",
                "context": [
                    {"role": "user", "content": "什么是价值投资？"},
                    {"role": "assistant", "content": reply1}
                ]
            }

            response2 = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=request2,
                timeout=60
            )

            elapsed2 = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed2:.2f}秒", "INFO")

            if response2.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"对话2失败: HTTP {response2.status_code}")
                self.log(f"❌ 对话2失败: {response2.status_code}", "ERROR")
                return result

            data2 = response2.json()
            reply2 = data2["data"]["reply"]

            self.log(f"🤖 AI回复2: {reply2[:150]}...", "INFO")

            # 第三轮对话（带股票上下文）
            self.log("\n💬 测试对话3 (带股票上下文): 贵州茅台适合加仓吗？", "INFO")
            start_time = time.time()

            request3 = {
                "message": "现在适合加仓吗？",
                "symbol": "600519",
                "stock_name": "贵州茅台",
                "context": []
            }

            response3 = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=request3,
                timeout=60
            )

            elapsed3 = time.time() - start_time
            self.log(f"⏱️  响应时间: {elapsed3:.2f}秒", "INFO")

            if response3.status_code != 200:
                result["status"] = "FAILED"
                result["errors"].append(f"对话3失败: HTTP {response3.status_code}")
                self.log(f"❌ 对话3失败: {response3.status_code}", "ERROR")
                return result

            data3 = response3.json()
            reply3 = data3["data"]["reply"]

            self.log(f"🤖 AI回复3: {reply3[:150]}...", "INFO")

            # 验证回复包含股票信息
            if "600519" in reply3 or "贵州茅台" in reply3:
                self.log("✅ AI回复正确包含股票上下文", "SUCCESS")
            else:
                self.log("⚠️  警告: AI回复可能未使用股票上下文", "WARNING")

            # 记录成功
            result["status"] = "PASSED"
            result["details"].append({
                "rounds": 3,
                "avg_response_time": (elapsed1 + elapsed2 + elapsed3) / 3
            })

            self.log("\n✅ TC-002 测试通过", "SUCCESS")

        except requests.Timeout:
            result["status"] = "FAILED"
            result["errors"].append("请求超时")
            self.log("❌ 请求超时", "ERROR")
        except Exception as e:
            result["status"] = "FAILED"
            result["errors"].append(str(e))
            self.log(f"❌ 测试异常: {e}", "ERROR")

        self.test_results.append(result)
        return result

    def test_error_handling(self) -> Dict[str, Any]:
        """TC-004: 测试错误处理"""
        self.log("\n" + "="*60, "INFO")
        self.log("TC-004: 网络异常错误处理测试", "INFO")
        self.log("="*60, "INFO")

        result = {
            "test_case": "TC-004",
            "name": "错误处理",
            "status": "PENDING",
            "details": [],
            "errors": []
        }

        try:
            # 测试1: 缺少必需参数
            self.log("🔍 测试1: 缺少必需参数", "INFO")
            response = requests.post(
                f"{self.base_url}/api/v1/ai/single-analysis",
                json={},  # 空数据
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code in [400, 422]:  # Bad Request or Unprocessable Entity
                self.log("✅ 正确返回错误状态码", "SUCCESS")
                result["details"].append("缺少参数检测: PASSED")
            else:
                self.log(f"⚠️  预期400/422，实际{response.status_code}", "WARNING")
                result["details"].append(f"缺少参数检测: 状态码{response.status_code}")

            # 测试2: 无效股票代码
            self.log("\n🔍 测试2: 无效股票代码", "INFO")
            response = requests.post(
                f"{self.base_url}/api/v1/ai/single-analysis",
                json={
                    "symbol": "999999",  # 不存在的代码
                    "stock_name": "不存在的股票",
                    "dimensions": ["fundamentals"],
                    "include_fundamentals": True,
                    "include_technicals": False
                },
                headers=self.get_headers(),
                timeout=30
            )

            # 可能返回200但数据为空，或返回404
            if response.status_code in [200, 404, 400]:
                self.log(f"✅ API正确处理无效股票代码 (HTTP {response.status_code})", "SUCCESS")
                result["details"].append("无效股票代码: PASSED")
            else:
                self.log(f"⚠️  意外状态码: {response.status_code}", "WARNING")

            result["status"] = "PASSED"
            self.log("\n✅ TC-004 测试通过", "SUCCESS")

        except Exception as e:
            result["status"] = "FAILED"
            result["errors"].append(str(e))
            self.log(f"❌ 测试异常: {e}", "ERROR")

        self.test_results.append(result)
        return result

    def generate_report(self):
        """生成测试报告"""
        self.log("\n" + "="*60, "INFO")
        self.log("📊 测试报告", "INFO")
        self.log("="*60, "INFO")

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = sum(1 for r in self.test_results if r["status"] == "FAILED")

        self.log(f"\n总计: {total} 个测试用例", "INFO")
        self.log(f"通过: {passed} 个", "SUCCESS")
        self.log(f"失败: {failed} 个", "ERROR" if failed > 0 else "INFO")
        self.log(f"通过率: {(passed/total*100) if total > 0 else 0:.1f}%", "INFO")

        # 详细结果
        self.log("\n详细结果:", "INFO")
        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASSED" else "❌"
            self.log(f"{status_symbol} {result['test_case']}: {result['name']} - {result['status']}",
                    "SUCCESS" if result["status"] == "PASSED" else "ERROR")

            if result["errors"]:
                for error in result["errors"]:
                    self.log(f"   错误: {error}", "ERROR")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed/total*100) if total > 0 else 0,
            "results": self.test_results
        }


def main():
    """主函数"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("前端AI集成自动化测试")
    print(f"{'='*60}{Colors.END}\n")

    tester = AIIntegrationTester()

    # 1. 健康检查
    if not tester.test_health():
        print(f"\n{Colors.RED}❌ 后端服务不可用，退出测试{Colors.END}")
        return

    # 2. 注册并登录
    if not tester.register_and_login():
        print(f"\n{Colors.RED}❌ 认证失败，退出测试{Colors.END}")
        return

    # 3. 执行测试用例
    tester.test_single_analysis()  # TC-001
    tester.test_chat()             # TC-002 (已跳过：API路径不匹配)
    tester.test_error_handling()   # TC-004

    # 4. 生成报告
    report = tester.generate_report()

    # 5. 返回状态码
    exit(0 if report["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
