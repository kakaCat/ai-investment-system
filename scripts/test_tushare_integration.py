#!/usr/bin/env python3
"""
Tushare数据源集成测试脚本

测试:
1. Tushare/AkShare连接状态
2. 实时行情数据获取
3. 基本面数据获取
4. 技术指标获取
5. AI Prompt数据格式化
"""

import asyncio
import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.utils.tushare_client import tushare_client


async def test_connection_status():
    """测试连接状态"""
    print("\n" + "="*60)
    print("测试 1: 数据源连接状态")
    print("="*60)

    if tushare_client.use_tushare:
        print("✅ Tushare API: 已连接")
        print("   推荐使用Tushare获取专业金融数据")
    elif tushare_client.use_akshare:
        print("✅ AkShare: 已连接")
        print("   使用免费的AkShare数据源")
    else:
        print("⚠️  数据源未配置，将使用Mock数据")
        print("\n   配置方法:")
        print("   1. Tushare (推荐): export TUSHARE_TOKEN=your_token")
        print("      获取Token: https://tushare.pro/register")
        print("   2. AkShare (免费): pip install akshare")

    return tushare_client.use_tushare or tushare_client.use_akshare


async def test_realtime_quote():
    """测试实时行情获取"""
    print("\n" + "="*60)
    print("测试 2: 实时行情数据获取")
    print("="*60)

    test_symbols = ["600519", "000858", "600600"]

    for symbol in test_symbols:
        print(f"\n获取 {symbol} 的实时行情...")

        try:
            quote = await tushare_client.get_realtime_quote(symbol)

            if quote:
                print(f"✅ 数据获取成功")
                print(f"   数据来源: {quote.get('data_source')}")
                print(f"   最新价: {quote.get('current_price')} 元")
                print(f"   涨跌幅: {quote.get('change_percent')}%")
                print(f"   成交量: {quote.get('volume') / 100:.2f if quote.get('volume') else 0} 手")

                # 检查是否是Mock数据
                if quote.get('data_source') == 'mock':
                    print("   ⚠️  返回的是Mock数据")
                    return False
                else:
                    print("   ✅ 真实数据")
            else:
                print(f"❌ 获取失败")
                return False

        except Exception as e:
            print(f"❌ 异常: {e}")
            return False

    return True


async def test_fundamentals():
    """测试基本面数据获取"""
    print("\n" + "="*60)
    print("测试 3: 基本面数据获取")
    print("="*60)

    symbol = "600519"
    print(f"\n获取 {symbol} 的基本面数据...")

    try:
        fundamentals = await tushare_client.get_fundamentals(symbol)

        if fundamentals:
            print(f"✅ 数据获取成功")
            print(f"   数据来源: {fundamentals.get('data_source')}")
            print(f"   市盈率(PE): {fundamentals.get('pe_ratio')}")
            print(f"   市净率(PB): {fundamentals.get('pb_ratio')}")
            market_cap = fundamentals.get('total_market_cap', 0)
            market_cap_yi = (market_cap / 10000) if market_cap else 0
            print(f"   总市值: {market_cap_yi:.2f} 亿元")

            if fundamentals.get('data_source') == 'mock':
                print("   ⚠️  返回的是Mock数据")
                return False
            else:
                print("   ✅ 真实数据")
                return True
        else:
            print(f"❌ 获取失败")
            return False

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


async def test_technical_indicators():
    """测试技术指标获取"""
    print("\n" + "="*60)
    print("测试 4: 技术指标获取")
    print("="*60)

    symbol = "600519"
    print(f"\n获取 {symbol} 的技术指标...")

    try:
        technicals = await tushare_client.get_technical_indicators(symbol)

        if technicals:
            print(f"✅ 数据获取成功")
            print(f"   数据来源: {technicals.get('data_source')}")
            print(f"   MA5: {technicals.get('ma5')} 元")
            print(f"   MA10: {technicals.get('ma10')} 元")
            print(f"   MA20: {technicals.get('ma20')} 元")
            print(f"   MA60: {technicals.get('ma60')} 元")

            if technicals.get('data_source') == 'mock':
                print("   ⚠️  返回的是Mock数据")
                return False
            else:
                print("   ✅ 真实数据")
                return True
        else:
            print(f"❌ 获取失败")
            return False

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


async def test_stock_info():
    """测试股票信息获取"""
    print("\n" + "="*60)
    print("测试 5: 股票基本信息获取")
    print("="*60)

    symbol = "600519"
    print(f"\n获取 {symbol} 的基本信息...")

    try:
        info = await tushare_client.get_stock_info(symbol)

        if info:
            print(f"✅ 数据获取成功")
            print(f"   数据来源: {info.get('data_source')}")
            print(f"   股票名称: {info.get('name')}")
            print(f"   所属行业: {info.get('industry')}")
            print(f"   上市板块: {info.get('market')}")

            if info.get('data_source') == 'mock':
                print("   ⚠️  返回的是Mock数据")
                return False
            else:
                print("   ✅ 真实数据")
                return True
        else:
            print(f"❌ 获取失败")
            return False

    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


async def test_comprehensive_data():
    """测试综合数据获取（模拟AI分析场景）"""
    print("\n" + "="*60)
    print("测试 6: 综合数据获取（AI分析场景）")
    print("="*60)

    symbol = "600519"
    print(f"\n模拟AI分析场景：获取 {symbol} 的完整数据...\n")

    stock_data = {}

    # 1. 行情数据
    quote = await tushare_client.get_realtime_quote(symbol)
    if quote:
        stock_data["quote"] = quote
        print(f"✅ 行情数据: 最新价 {quote.get('current_price')} 元, 涨跌 {quote.get('change_percent')}%")

    # 2. 基本面数据
    fundamentals = await tushare_client.get_fundamentals(symbol)
    if fundamentals:
        stock_data["fundamentals"] = fundamentals
        print(f"✅ 基本面: PE={fundamentals.get('pe_ratio')}, PB={fundamentals.get('pb_ratio')}")

    # 3. 技术指标
    technicals = await tushare_client.get_technical_indicators(symbol)
    if technicals:
        stock_data["technicals"] = technicals
        print(f"✅ 技术面: MA5={technicals.get('ma5')}, MA20={technicals.get('ma20')}")

    # 4. 股票信息
    info = await tushare_client.get_stock_info(symbol)
    if info:
        stock_data["info"] = info
        print(f"✅ 股票信息: {info.get('name')} ({info.get('industry')})")

    print(f"\n综合数据获取完成，共 {len(stock_data)} 个数据集")

    # 检查数据来源
    all_real = True
    for key, value in stock_data.items():
        if value.get('data_source') == 'mock':
            all_real = False
            break

    if all_real and stock_data:
        print("✅ 所有数据均为真实数据")
        return True
    elif stock_data:
        print("⚠️  部分数据为Mock")
        return False
    else:
        print("❌ 未获取到任何数据")
        return False


async def main():
    """主函数"""
    print("="*60)
    print("🧪 Tushare数据源集成测试")
    print("="*60)

    results = {}

    # 测试1: 连接状态
    results["连接状态"] = await test_connection_status()

    if not results["连接状态"]:
        print("\n" + "="*60)
        print("⚠️  测试中止")
        print("="*60)
        print("数据源未配置，无法继续测试")
        print("\n配置步骤:")
        print("1. 获取Tushare Token: https://tushare.pro/register")
        print("2. 配置环境变量: export TUSHARE_TOKEN=your_token")
        print("3. 或者安装AkShare: pip install akshare")
        return 1

    # 测试2-6
    results["实时行情"] = await test_realtime_quote()
    results["基本面数据"] = await test_fundamentals()
    results["技术指标"] = await test_technical_indicators()
    results["股票信息"] = await test_stock_info()
    results["综合数据"] = await test_comprehensive_data()

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15s}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！数据源集成成功")
        print("\n✅ AI分析可以使用真实股票数据")
        print("\n下一步:")
        print("1. 安装依赖: pip install tushare akshare pandas numpy")
        print("2. 启动后端: ./scripts/dev.sh")
        print("3. 测试AI分析: python scripts/test_ai_features.py")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败")
        print("请检查数据源配置")
        return 1


if __name__ == "__main__":
    print("\n提示:")
    print("1. 确保已安装: pip install tushare akshare pandas numpy")
    print("2. Tushare用户: export TUSHARE_TOKEN=your_token")
    print("3. 或使用免费的AkShare（无需配置）")
    print("\n按Enter键开始测试...")
    input()

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
