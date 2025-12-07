#!/usr/bin/env python3
"""
AI功能验证脚本 - 快速检查AI配置是否正确

测试项:
1. Ollama服务状态
2. DeepSeek API配置
3. AI客户端基本功能
4. 简单的AI调用测试
"""

import asyncio
import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.utils.ai_client import ai_client, AIPromptBuilder


async def check_ollama():
    """检查Ollama状态"""
    print("\n" + "="*60)
    print("1. 检查Ollama服务")
    print("="*60)

    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Ollama运行正常")
                print(f"   可用模型数: {len(models)}")
                if models:
                    print(f"   模型列表:")
                    for model in models[:5]:
                        print(f"     - {model['name']}")
                return True
            else:
                print(f"⚠️  Ollama响应异常: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ollama未运行或无法连接")
        print(f"   错误: {e}")
        print(f"   提示: 运行 'ollama serve' 启动服务")
        return False


async def check_deepseek():
    """检查DeepSeek配置"""
    print("\n" + "="*60)
    print("2. 检查DeepSeek API配置")
    print("="*60)

    deepseek_key = ai_client.deepseek_key
    if deepseek_key:
        print(f"✅ DeepSeek API Key已配置")
        print(f"   Key: {deepseek_key[:10]}...{deepseek_key[-4:]}")
        return True
    else:
        print(f"⚠️  DeepSeek API Key未配置")
        print(f"   可在 backend/.env 中添加:")
        print(f"   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx")
        return False


async def test_ai_call():
    """测试AI调用"""
    print("\n" + "="*60)
    print("3. 测试AI调用")
    print("="*60)

    try:
        print("发送测试消息...")
        messages = [
            {"role": "system", "content": "你是一个投资分析助手。"},
            {"role": "user", "content": "用一句话介绍贵州茅台"}
        ]

        response = await ai_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        print(f"\n✅ AI调用成功")
        print(f"   响应内容: {response[:150]}...")

        # 检查是否是Mock数据
        if "请配置" in response or "Mock" in response:
            print(f"\n⚠️  当前返回的是Mock数据")
            print(f"   原因: Ollama未运行且DeepSeek未配置")
            return False
        else:
            print(f"\n✅ 真实AI响应")
            return True

    except Exception as e:
        print(f"❌ AI调用失败")
        print(f"   错误: {e}")
        return False


async def test_stock_analysis_prompt():
    """测试股票分析Prompt构建"""
    print("\n" + "="*60)
    print("4. 测试Prompt构建")
    print("="*60)

    try:
        messages = AIPromptBuilder.build_stock_analysis_prompt(
            symbol="600519",
            stock_name="贵州茅台",
            stock_data=None,
            include_fundamentals=True,
            include_technicals=True,
            include_valuation=True
        )

        print(f"✅ Prompt构建成功")
        print(f"   消息数: {len(messages)}")
        print(f"   系统消息长度: {len(messages[0]['content'])}")
        print(f"   用户消息长度: {len(messages[1]['content'])}")
        return True
    except Exception as e:
        print(f"❌ Prompt构建失败: {e}")
        return False


async def main():
    """主函数"""
    print("="*60)
    print("🔍 AI功能配置验证")
    print("="*60)

    results = []

    # 1. 检查Ollama
    ollama_ok = await check_ollama()
    results.append(("Ollama服务", ollama_ok))

    # 2. 检查DeepSeek
    deepseek_ok = await check_deepseek()
    results.append(("DeepSeek配置", deepseek_ok))

    # 3. 测试AI调用
    ai_call_ok = await test_ai_call()
    results.append(("AI调用测试", ai_call_ok))

    # 4. 测试Prompt构建
    prompt_ok = await test_stock_analysis_prompt()
    results.append(("Prompt构建", prompt_ok))

    # 总结
    print("\n" + "="*60)
    print("📊 验证结果总结")
    print("="*60)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:20s}: {status}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\n总计: {passed}/{total} 通过")

    # 建议
    print("\n" + "="*60)
    print("💡 建议")
    print("="*60)

    if not ollama_ok and not deepseek_ok:
        print("⚠️  AI后端未配置，将使用Mock数据")
        print("\n推荐操作:")
        print("1. 启动Ollama (推荐): ollama serve")
        print("2. 或配置DeepSeek API Key")
    elif ollama_ok:
        print("✅ Ollama运行正常，推荐使用")
        print("   - 免费")
        print("   - 本地运行")
        print("   - 数据隐私")
    elif deepseek_ok:
        print("✅ DeepSeek已配置")
        print("   - 云端API")
        print("   - 低成本")
        print("   - 响应快速")

    if passed == total:
        print("\n🎉 所有检查通过！AI功能已就绪")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项检查未通过")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
