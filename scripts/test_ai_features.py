#!/usr/bin/env python3
"""
AI功能端到端测试脚本

测试所有AI相关接口是否正常工作
"""

import asyncio
import httpx
import json
from typing import Optional


class AIFeatureTester:
    """AI功能测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.headers = {"Content-Type": "application/json"}

    async def login(self, username: str = "test@example.com", password: str = "password123"):
        """登录获取Token"""
        print("\n🔐 1. 测试登录...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data["data"]["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"   提示: 请先创建测试用户或使用正确的账号密码")
                return False

    async def test_single_analysis(self):
        """测试单股AI分析"""
        print("\n🤖 2. 测试单股AI分析...")

        request_data = {
            "symbol": "600519",
            "analysis_type": "comprehensive",
            "include_fundamentals": True,
            "include_technicals": True,
            "include_valuation": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ai/single-analysis",
                headers=self.headers,
                json=request_data
            )

            if response.status_code == 200:
                data = response.json()
                if data["code"] == 0:
                    result = data["data"]
                    print("✅ 单股分析成功")
                    print(f"   股票: {result['stock_name']} ({result['symbol']})")
                    print(f"   建议: {result['ai_suggestion'][:50]}...")
                    print(f"   置信度: {result['confidence_level']}")

                    # 检查是否是真实AI响应
                    suggestion = result.get('ai_suggestion', '')
                    if 'Mock' in suggestion or '请配置' in suggestion:
                        print("⚠️  警告: 返回的是Mock数据，AI可能未正确配置")
                    else:
                        print("✅ AI真实调用成功")

                    return True
                else:
                    print(f"❌ 分析失败: {data['message']}")
            else:
                print(f"❌ 请求失败: {response.status_code}")

        return False

    async def test_ai_chat(self):
        """测试AI对话"""
        print("\n💬 3. 测试AI对话...")

        # 步骤1: 创建会话
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ai/chat/session/create",
                headers=self.headers,
                json={"context_symbol": "600519"}
            )

            if response.status_code != 200:
                print(f"❌ 创建会话失败: {response.status_code}")
                return False

            session_data = response.json()["data"]
            session_id = session_data["session_id"]
            print(f"✅ 会话创建成功: {session_id[:8]}...")

            # 步骤2: 发送消息
            response = await client.post(
                f"{self.base_url}/api/v1/ai/chat/message/send",
                headers=self.headers,
                json={
                    "session_id": session_id,
                    "message": "简单分析一下贵州茅台的投资价值"
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data["code"] == 0:
                    reply = data["data"]["content"]
                    print("✅ AI对话成功")
                    print(f"   AI回复: {reply[:100]}...")

                    # 检查是否是真实AI响应
                    if 'Mock' in reply or '模拟' in reply:
                        print("⚠️  警告: 返回的是Mock数据")
                    else:
                        print("✅ AI真实对话成功")

                    return True
                else:
                    print(f"❌ 对话失败: {data['message']}")
            else:
                print(f"❌ 请求失败: {response.status_code}")

        return False

    async def test_batch_analysis(self):
        """测试批量分析"""
        print("\n📊 4. 测试批量AI分析...")

        request_data = {
            "stock_symbols": ["600519", "600600", "000858"]
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ai/daily-analysis/create",
                headers=self.headers,
                json=request_data
            )

            if response.status_code == 200:
                data = response.json()
                if data["code"] == 0:
                    result = data["data"]
                    print("✅ 批量分析成功")
                    print(f"   任务ID: {result['task_id'][:8]}...")
                    print(f"   状态: {result['status']}")
                    print(f"   处理: {result['processed_stocks']}/{result['total_stocks']}")

                    if result.get('results'):
                        print(f"   结果数: {len(result['results'])}")

                    return True
                else:
                    print(f"❌ 批量分析失败: {data['message']}")
            else:
                print(f"❌ 请求失败: {response.status_code}")

        return False

    async def test_daily_review(self):
        """测试每日复盘"""
        print("\n📝 5. 测试每日复盘...")

        # 先生成复盘
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ai/review/generate",
                headers=self.headers,
                json={}
            )

            if response.status_code == 200:
                data = response.json()
                if data["code"] == 0:
                    result = data["data"]
                    print("✅ 复盘生成成功")
                    print(f"   状态: {result.get('status')}")
                    print(f"   复盘ID: {result.get('review_id')}")
                    return True
                else:
                    print(f"❌ 复盘生成失败: {data['message']}")
            else:
                print(f"❌ 请求失败: {response.status_code}")

        return False

    async def check_ollama(self):
        """检查Ollama是否运行"""
        print("\n🔍 检查AI后端状态...")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    print("✅ Ollama运行中")
                    models = response.json().get("models", [])
                    if models:
                        print(f"   可用模型: {', '.join([m['name'] for m in models[:3]])}")
                    return True
        except:
            pass

        print("⚠️  Ollama未运行")
        print("   提示: 运行 'ollama serve' 启动本地模型")
        print("   或配置DEEPSEEK_API_KEY使用云端API")
        return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 AI功能端到端测试")
        print("=" * 60)

        # 检查Ollama
        await self.check_ollama()

        # 登录
        if not await self.login():
            print("\n❌ 无法继续测试，请先配置好用户登录")
            return

        # 运行各项测试
        results = {
            "单股分析": await self.test_single_analysis(),
            "AI对话": await self.test_ai_chat(),
            "批量分析": await self.test_batch_analysis(),
            "每日复盘": await self.test_daily_review(),
        }

        # 总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)

        total = len(results)
        passed = sum(1 for v in results.values() if v)

        for name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{name}: {status}")

        print(f"\n总计: {passed}/{total} 通过")

        if passed == total:
            print("\n🎉 所有AI功能测试通过！")
        else:
            print(f"\n⚠️  有 {total - passed} 项测试失败，请检查配置")


async def main():
    """主函数"""
    tester = AIFeatureTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("\n提示:")
    print("1. 确保后端服务运行中: ./scripts/dev.sh")
    print("2. 确保Ollama运行或配置了DEEPSEEK_API_KEY")
    print("3. 确保已创建测试用户（test@example.com / password123）")
    print("\n按Enter键开始测试...")
    input()

    asyncio.run(main())
