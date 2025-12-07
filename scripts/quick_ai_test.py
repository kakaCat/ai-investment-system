#!/usr/bin/env python3
"""
快速AI测试 - 不依赖完整的应用配置

直接测试Ollama和AI调用功能
"""

import asyncio
import sys
import httpx
import json
import os


async def test_ollama_connection():
    """测试Ollama连接"""
    print("\n" + "="*60)
    print("测试 1: Ollama服务连接")
    print("="*60)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Ollama运行正常")
                print(f"   端口: 11434")
                print(f"   可用模型数: {len(models)}")
                if models:
                    print(f"\n   可用模型:")
                    for model in models:
                        size_gb = model['size'] / (1024**3)
                        print(f"     • {model['name']:30s} ({size_gb:.1f} GB)")
                return True, models
            else:
                print(f"❌ Ollama响应异常: {response.status_code}")
                return False, []
    except Exception as e:
        print(f"❌ Ollama连接失败")
        print(f"   错误: {e}")
        print(f"\n   💡 解决方案:")
        print(f"      1. 安装Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print(f"      2. 启动服务: ollama serve")
        print(f"      3. 下载模型: ollama pull qwen2.5:7b")
        return False, []


async def test_ollama_chat(model_name="qwen2:latest"):
    """测试Ollama对话功能"""
    print("\n" + "="*60)
    print(f"测试 2: Ollama对话测试 (模型: {model_name})")
    print("="*60)

    try:
        print(f"发送测试消息...")

        request_data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业的投资分析助手。"},
                {"role": "user", "content": "用一句话介绍贵州茅台"}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 100
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json=request_data
            )

            if response.status_code == 200:
                data = response.json()
                ai_reply = data.get("message", {}).get("content", "")

                print(f"✅ AI调用成功")
                print(f"\n   AI回复:")
                print(f"   {ai_reply}")
                print(f"\n   模型: {data.get('model')}")
                print(f"   耗时: ~{data.get('total_duration', 0) / 1e9:.2f}秒")

                return True, ai_reply
            else:
                print(f"❌ AI调用失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return False, None

    except Exception as e:
        print(f"❌ AI调用异常")
        print(f"   错误: {e}")
        return False, None


async def test_stock_analysis_prompt():
    """测试股票分析Prompt"""
    print("\n" + "="*60)
    print("测试 3: 股票分析Prompt")
    print("="*60)

    prompt = """你是一个专业的AI投资分析师。请对以下股票进行综合分析，并以JSON格式返回结果。

**股票信息**:
- 股票代码: 600519
- 股票名称: 贵州茅台

**分析要求**:
请提供以下维度的分析:
1. 基本面分析 (fundamental_score: 0-100分)
2. 技术面分析 (technical_score: 0-100分)
3. 估值分析 (valuation_score: 0-100分)
4. 综合评分 (overall_score: 0-100分)
5. 投资建议 (ai_suggestion: 字符串)
6. 投资理由 (ai_reasons: 字符串数组)
7. 置信度 (confidence_level: 0-100)

**输出格式** (必须严格遵守JSON格式):
```json
{
  "ai_score": {
    "fundamental_score": 75,
    "technical_score": 68,
    "valuation_score": 82,
    "overall_score": 75
  },
  "ai_suggestion": "建议持有，中长期看好",
  "ai_strategy": {
    "target_price": 1800.0,
    "recommended_position": 15.0,
    "risk_level": "medium",
    "holding_period": "6-12个月",
    "stop_loss_price": 1500.0
  },
  "ai_reasons": ["理由1", "理由2", "理由3"],
  "confidence_level": 78.5
}
```

请只返回JSON，不要有其他文字。
"""

    print(f"✅ Prompt构建成功")
    print(f"   Prompt长度: {len(prompt)} 字符")
    print(f"\n   Prompt预览:")
    print(f"   {prompt[:200]}...")

    return True, prompt


async def test_full_stock_analysis(model_name="qwen2:latest"):
    """完整的股票分析测试"""
    print("\n" + "="*60)
    print(f"测试 4: 完整股票分析流程")
    print("="*60)

    _, prompt = await test_stock_analysis_prompt()

    print(f"\n正在调用AI进行股票分析...")
    print(f"(这可能需要5-10秒)")

    try:
        request_data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业的投资分析师，精通股票分析。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json=request_data
            )

            if response.status_code == 200:
                data = response.json()
                ai_reply = data.get("message", {}).get("content", "")

                print(f"\n✅ 股票分析成功")
                print(f"\n   AI分析结果:")
                print(f"   {ai_reply[:500]}...")

                # 尝试解析JSON
                try:
                    # 提取JSON
                    if "```json" in ai_reply:
                        start = ai_reply.find("```json") + 7
                        end = ai_reply.find("```", start)
                        json_str = ai_reply[start:end].strip()
                    elif "```" in ai_reply:
                        start = ai_reply.find("```") + 3
                        end = ai_reply.find("```", start)
                        json_str = ai_reply[start:end].strip()
                    elif "{" in ai_reply:
                        start = ai_reply.find("{")
                        end = ai_reply.rfind("}") + 1
                        json_str = ai_reply[start:end]
                    else:
                        json_str = ai_reply

                    result = json.loads(json_str)
                    print(f"\n   ✅ JSON解析成功")
                    print(f"   综合评分: {result.get('ai_score', {}).get('overall_score', 'N/A')}")
                    print(f"   投资建议: {result.get('ai_suggestion', 'N/A')}")
                    print(f"   置信度: {result.get('confidence_level', 'N/A')}")

                    return True, result

                except Exception as e:
                    print(f"\n   ⚠️  JSON解析失败: {e}")
                    print(f"   但AI调用成功，可能需要优化Prompt")
                    return True, None

            else:
                print(f"❌ 分析失败: {response.status_code}")
                return False, None

    except Exception as e:
        print(f"❌ 分析异常: {e}")
        return False, None


async def check_deepseek_config():
    """检查DeepSeek配置"""
    print("\n" + "="*60)
    print("检查 DeepSeek API配置")
    print("="*60)

    # 尝试从环境变量或.env文件读取
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if deepseek_key:
        print(f"✅ DeepSeek API Key已配置")
        print(f"   Key: {deepseek_key[:10]}...{deepseek_key[-4:]}")
        return True
    else:
        print(f"ℹ️  DeepSeek API Key未配置")
        print(f"   如需使用DeepSeek API，请在 backend/.env 中添加:")
        print(f"   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx")
        return False


async def main():
    """主函数"""
    print("="*60)
    print("🚀 AI功能快速测试")
    print("="*60)

    # 测试Ollama连接
    ollama_ok, models = await test_ollama_connection()

    if not ollama_ok:
        print("\n" + "="*60)
        print("⚠️  测试中止")
        print("="*60)
        print("Ollama未运行，无法继续测试")
        print("\n请先:")
        print("1. 安装并启动Ollama")
        print("2. 下载模型: ollama pull qwen2.5:7b")
        return 1

    # 选择模型
    model_name = None
    for model in models:
        name = model['name']
        if 'qwen2' in name.lower() or 'deepseek' in name.lower():
            if 'vl' not in name.lower():  # 跳过视觉模型
                model_name = name
                break

    if not model_name and models:
        model_name = models[0]['name']

    print(f"\n使用模型: {model_name}")

    # 测试对话
    chat_ok, _ = await test_ollama_chat(model_name)

    if chat_ok:
        # 测试完整股票分析
        await test_full_stock_analysis(model_name)

    # 检查DeepSeek配置
    await check_deepseek_config()

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    if ollama_ok and chat_ok:
        print("✅ Ollama连接正常")
        print("✅ AI对话功能正常")
        print("✅ 可以开始使用AI功能")
        print("\n下一步:")
        print("1. 启动后端: ./scripts/dev.sh")
        print("2. 运行完整测试: python scripts/test_ai_features.py")
        return 0
    else:
        print("⚠️  部分测试失败")
        print("请检查配置")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
