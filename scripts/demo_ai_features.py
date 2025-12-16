#!/usr/bin/env python3
"""
AI功能演示脚本

快速演示系统的AI投资分析功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from app.utils.ai_client import ai_client


async def demo_single_stock_analysis():
    """演示单股AI分析"""
    print("\n" + "="*60)
    print("🤖 演示1: 单股AI分析")
    print("="*60)

    print("\n正在分析: 贵州茅台 (600519)")
    print("分析维度: 基本面 + 技术面 + 估值")
    print("预计耗时: 30秒...\n")

    messages = [
        {
            "role": "system",
            "content": "你是一位专业的投资分析师。请基于提供的股票信息进行分析。"
        },
        {
            "role": "user",
            "content": """请分析贵州茅台(600519)的投资价值。

股票信息:
- 股票代码: 600519
- 股票名称: 贵州茅台
- 当前价格: 1580元
- 市盈率: 32
- 市净率: 10.5
- 行业: 白酒

请从以下维度评分(0-100):
1. 基本面评分
2. 技术面评分
3. 估值评分
4. 综合评分

并给出投资建议和置信度(0-100)。

请用JSON格式返回:
{
  "ai_score": {
    "fundamental_score": 数字,
    "technical_score": 数字,
    "valuation_score": 数字,
    "overall_score": 数字
  },
  "ai_suggestion": "建议文本",
  "confidence_level": 数字
}"""
        }
    ]

    try:
        reply = await ai_client.chat_completion(messages)
        print("✅ 分析完成!\n")
        print("AI回复:")
        print("-" * 60)
        print(reply)
        print("-" * 60)
    except Exception as e:
        print(f"❌ 分析失败: {e}")


async def demo_ai_chat():
    """演示AI投资对话"""
    print("\n" + "="*60)
    print("💬 演示2: AI投资对话")
    print("="*60)

    questions = [
        "什么是价值投资?",
        "如何判断一只股票是否值得投资?",
        "什么时候应该止损?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("AI回复中...\n")

        messages = [
            {
                "role": "system",
                "content": "你是一位专业的投资顾问,擅长用简洁易懂的语言解释投资概念。"
            },
            {
                "role": "user",
                "content": question
            }
        ]

        try:
            reply = await ai_client.chat_completion(messages)
            print("回复:")
            print("-" * 60)
            # 只显示前300字符
            if len(reply) > 300:
                print(reply[:300] + "...\n(回复已截断)")
            else:
                print(reply)
            print("-" * 60)
        except Exception as e:
            print(f"❌ 对话失败: {e}")

        if i < len(questions):
            print("\n等待2秒继续下一个问题...")
            await asyncio.sleep(2)


async def demo_batch_analysis():
    """演示批量分析"""
    print("\n" + "="*60)
    print("📊 演示3: 批量股票分析")
    print("="*60)

    stocks = [
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("600600", "青岛啤酒")
    ]

    print(f"\n准备分析 {len(stocks)} 只股票:")
    for symbol, name in stocks:
        print(f"  - {name} ({symbol})")

    print("\n批量分析功能说明:")
    print("  • 并行分析多只股票")
    print("  • 实时显示进度")
    print("  • 按评分排序结果")
    print("  • 支持导出CSV")
    print("\n(此演示不执行实际分析，仅展示功能)")


async def demo_daily_review():
    """演示每日复盘"""
    print("\n" + "="*60)
    print("📈 演示4: 每日市场复盘")
    print("="*60)

    print("\n每日复盘功能包含:")
    print("  ✅ 市场总结 (指数表现)")
    print("  ✅ 热点板块 (涨幅前3)")
    print("  ✅ 持仓表现 (今日盈亏)")
    print("  ✅ 重要事件影响分析")
    print("  ✅ 明日市场预测")
    print("  ✅ 未来一周展望")
    print("  ✅ AI观点 vs 用户观点对比")

    print("\n示例复盘内容:")
    print("-" * 60)
    print("📊 市场总结:")
    print("  上证指数: 3245.67 (+0.85%)")
    print("  成交量: 2850亿")
    print("\n🔥 热点板块:")
    print("  1. 新能源汽车 (+3.2%)")
    print("  2. 人工智能 (+2.8%)")
    print("  3. ChatGPT概念 (+2.5%)")
    print("\n💼 持仓表现:")
    print("  今日盈亏: +¥3,200 (+0.92%)")
    print("  涨幅第一: 比亚迪 +2.3%")
    print("\n🔮 明日预测:")
    print("  预计震荡上行，关注3,250-3,280区间")
    print("-" * 60)


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "="*60)
    print("🎉 AI投资管理系统 - 功能演示")
    print("="*60)
    print("\n本演示将展示以下AI功能:")
    print("  1. 🤖 单股AI分析")
    print("  2. 💬 AI投资对话")
    print("  3. 📊 批量股票分析")
    print("  4. 📈 每日市场复盘")
    print("\n提示: 部分演示需要DeepSeek API Key")


def print_summary():
    """打印总结"""
    print("\n" + "="*60)
    print("✅ 演示完成!")
    print("="*60)
    print("\n🚀 如何启动完整系统:")
    print("  1. 配置API Key (DEEPSEEK_API_KEY)")
    print("  2. 运行: ./scripts/dev.sh")
    print("  3. 访问: http://localhost:5175")
    print("\n📚 更多信息:")
    print("  • 快速启动: QUICK-START.md")
    print("  • 开发指南: CLAUDE.md")
    print("  • 完成报告: management/SPRINT-002-COMPLETION-REPORT.md")
    print("\n💡 功能体验:")
    print("  • 股票详情页 → 点击 '🤖 AI分析'")
    print("  • 左侧菜单 → 💬 AI对话")
    print("  • 左侧菜单 → 📊 每日复盘")


async def main():
    """主函数"""
    print_welcome()

    # 检查API Key
    if not ai_client.api_key:
        print("\n⚠️  警告: 未配置 DEEPSEEK_API_KEY")
        print("   部分演示将跳过实际API调用")
        print("   请设置环境变量: export DEEPSEEK_API_KEY='your-key'\n")
        skip_api = True
    else:
        print("\n✅ DeepSeek API Key 已配置")
        skip_api = False

    input("\n按 Enter 开始演示...")

    # 演示1: 单股分析
    if not skip_api:
        await demo_single_stock_analysis()
        input("\n按 Enter 继续...")
    else:
        print("\n(跳过单股分析演示 - 需要API Key)")

    # 演示2: AI对话
    if not skip_api:
        await demo_ai_chat()
        input("\n按 Enter 继续...")
    else:
        print("\n(跳过AI对话演示 - 需要API Key)")

    # 演示3: 批量分析
    await demo_batch_analysis()
    input("\n按 Enter 继续...")

    # 演示4: 每日复盘
    await demo_daily_review()

    # 总结
    print_summary()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n演示已取消")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
