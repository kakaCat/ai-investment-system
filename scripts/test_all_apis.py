#!/usr/bin/env python3
"""
全接口测试脚本

测试所有后端API接口，发现并报告问题
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

BASE_URL = "http://localhost:8000"
DEV_TOKEN = "dev-token"

# 测试结果统计
test_results = {
    "passed": 0,
    "failed": 0,
    "errors": []
}

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_api(
    name: str,
    endpoint: str,
    data: Dict,
    expected_status: int = 200,
    headers: Optional[Dict] = None,
    skip_auth: bool = False
) -> bool:
    """
    测试API接口

    Returns:
        bool: 测试是否通过
    """
    if headers is None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEV_TOKEN}"
        } if not skip_auth else {"Content-Type": "application/json"}

    print(f"\n[{name}]")
    print(f"  请求: POST {endpoint}")
    print(f"  数据: {json.dumps(data, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=10
        )

        status = response.status_code
        print(f"  状态: {status}", end="")

        if status == expected_status:
            print(" ✅")
            test_results["passed"] += 1

            # 打印响应摘要
            try:
                resp_data = response.json()
                if status == 200 and "data" in resp_data:
                    print(f"  响应: 成功 (code={resp_data.get('code', 0)})")
            except:
                pass

            return True
        else:
            print(f" ❌ (预期{expected_status})")
            test_results["failed"] += 1
            test_results["errors"].append({
                "name": name,
                "endpoint": endpoint,
                "expected": expected_status,
                "actual": status,
                "response": response.text[:200]
            })

            # 打印错误详情
            try:
                error_data = response.json()
                print(f"  错误: {json.dumps(error_data, ensure_ascii=False, indent=4)}")
            except:
                print(f"  错误: {response.text[:200]}")

            return False

    except Exception as e:
        print(f" ❌ 异常")
        print(f"  错误: {str(e)}")
        test_results["failed"] += 1
        test_results["errors"].append({
            "name": name,
            "endpoint": endpoint,
            "error": str(e)
        })
        return False

def test_backend_health():
    """测试后端健康状态"""
    print_section("0. 后端健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        print(f"✅ 后端状态: {data}")
        return True
    except Exception as e:
        print(f"❌ 后端无法访问: {e}")
        print("\n请先启动后端: ./scripts/dev.sh")
        return False

def test_account_apis():
    """测试账户管理接口"""
    print_section("1. 账户管理接口 (Account)")

    timestamp = datetime.now().strftime('%H%M%S')

    # 1.1 创建账户 - 最小参数
    account_id = None
    result = test_api(
        "创建账户 (最小参数)",
        "/api/v1/account/create",
        {
            "account_name": f"测试账户_{timestamp}",
            "market": "A-share"
        }
    )

    # 1.2 创建账户 - 完整参数
    result2 = test_api(
        "创建账户 (完整参数)",
        "/api/v1/account/create",
        {
            "account_name": f"完整账户_{timestamp}",
            "market": "A-share",
            "broker": "华泰证券",
            "account_number": "1234567890",
            "initial_capital": 100000.0
        }
    )

    # 1.3 查询账户列表
    test_api(
        "查询账户列表",
        "/api/v1/account/query",
        {
            "page": 1,
            "page_size": 20
        }
    )

    # 1.4 查询账户详情
    test_api(
        "查询账户详情",
        "/api/v1/account/detail",
        {
            "account_id": 1
        }
    )

    # 1.5 更新账户
    test_api(
        "更新账户",
        "/api/v1/account/update",
        {
            "account_id": 1,
            "account_name": f"更新账户_{timestamp}"
        }
    )

    # 1.6 删除账户 (可能失败 - 有持仓)
    test_api(
        "删除账户",
        "/api/v1/account/delete",
        {
            "account_id": 999  # 不存在的ID
        },
        expected_status=500  # 可能返回错误
    )

def test_holding_apis():
    """测试持仓管理接口"""
    print_section("2. 持仓管理接口 (Holding)")

    # 2.1 查询持仓列表
    test_api(
        "查询持仓列表",
        "/api/v1/holding/query",
        {
            "account_id": 1,
            "page": 1,
            "page_size": 20
        }
    )

    # 2.2 查询持仓详情
    test_api(
        "查询持仓详情",
        "/api/v1/holding/detail",
        {
            "holding_id": 1
        }
    )

    # 2.3 添加持仓
    test_api(
        "添加持仓",
        "/api/v1/holding/add",
        {
            "account_id": 1,
            "symbol": "600000.SH",
            "stock_name": "浦发银行",
            "quantity": 1000,
            "cost_price": 10.5
        }
    )

    # 2.4 更新持仓
    test_api(
        "更新持仓",
        "/api/v1/holding/update",
        {
            "holding_id": 1,
            "quantity": 1100,
            "available_quantity": 1100
        }
    )

    # 2.5 删除持仓
    test_api(
        "删除持仓",
        "/api/v1/holding/delete",
        {
            "holding_id": 999  # 不存在的ID
        },
        expected_status=500
    )

def test_trade_apis():
    """测试交易记录接口"""
    print_section("3. 交易记录接口 (Trade)")

    # 3.1 查询交易记录
    test_api(
        "查询交易记录",
        "/api/v1/trade/query",
        {
            "account_id": 1,
            "page": 1,
            "page_size": 20
        }
    )

    # 3.2 添加买入记录
    test_api(
        "添加买入记录",
        "/api/v1/trade/buy",
        {
            "account_id": 1,
            "symbol": "600519.SH",
            "stock_name": "贵州茅台",
            "quantity": 100,
            "price": 1580.0,
            "trade_date": "2025-12-09"
        }
    )

    # 3.3 添加卖出记录
    test_api(
        "添加卖出记录",
        "/api/v1/trade/sell",
        {
            "account_id": 1,
            "symbol": "600000.SH",
            "stock_name": "浦发银行",
            "quantity": 500,
            "price": 10.8,
            "trade_date": "2025-12-09"
        }
    )

def test_stock_apis():
    """测试股票数据接口"""
    print_section("4. 股票数据接口 (Stock)")

    # 4.1 搜索股票
    test_api(
        "搜索股票",
        "/api/v1/stock/search",
        {
            "keyword": "贵州茅台",
            "limit": 10
        }
    )

    # 4.2 获取股票详情
    test_api(
        "获取股票详情",
        "/api/v1/stock/detail",
        {
            "symbol": "600519.SH"
        }
    )

    # 4.3 获取股票行情
    test_api(
        "获取股票行情",
        "/api/v1/stock/quote",
        {
            "symbol": "600519.SH"
        }
    )

def test_ai_apis():
    """测试AI分析接口"""
    print_section("5. AI分析接口 (AI)")

    # 5.1 单股AI分析
    test_api(
        "单股AI分析",
        "/api/v1/ai/single-analysis",
        {
            "symbol": "600519.SH",
            "stock_name": "贵州茅台",
            "include_fundamentals": True,
            "include_technicals": True
        }
    )

    # 5.2 AI对话
    test_api(
        "AI对话",
        "/api/v1/ai/chat",
        {
            "message": "什么是价值投资？",
            "context": []
        }
    )

    # 5.3 创建批量分析任务
    test_api(
        "创建批量分析任务",
        "/api/v1/ai/daily-analysis/create",
        {
            "account_id": 1,
            "analysis_date": "2025-12-09"
        }
    )

    # 5.4 查询批量分析结果
    test_api(
        "查询批量分析结果",
        "/api/v1/ai/daily-analysis/results",
        {
            "account_id": 1,
            "analysis_date": "2025-12-09"
        }
    )

    # 5.5 获取每日复盘
    test_api(
        "获取每日复盘",
        "/api/v1/ai/review/get",
        {
            "account_id": 1,
            "review_date": "2025-12-09"
        }
    )

def test_event_apis():
    """测试事件管理接口"""
    print_section("6. 事件管理接口 (Event)")

    # 6.1 查询事件列表
    test_api(
        "查询事件列表",
        "/api/v1/event/query",
        {
            "page": 1,
            "page_size": 20
        }
    )

    # 6.2 添加事件
    test_api(
        "添加事件",
        "/api/v1/event/create",
        {
            "event_type": "policy",
            "title": "测试政策事件",
            "description": "这是一个测试事件",
            "event_date": "2025-12-09",
            "affected_stocks": ["600519.SH"]
        }
    )

def test_user_apis():
    """测试用户接口"""
    print_section("7. 用户接口 (User)")

    # 7.1 获取当前用户信息
    test_api(
        "获取当前用户信息",
        "/api/v1/user/me",
        {}
    )

    # 7.2 更新用户信息
    test_api(
        "更新用户信息",
        "/api/v1/user/update",
        {
            "nickname": "测试用户"
        }
    )

def test_validation_cases():
    """测试参数验证"""
    print_section("8. 参数验证测试")

    # 8.1 缺少必填字段
    test_api(
        "缺少account_name",
        "/api/v1/account/create",
        {
            "market": "A-share"
        },
        expected_status=422
    )

    # 8.2 字段类型错误
    test_api(
        "initial_capital为负数",
        "/api/v1/account/create",
        {
            "account_name": "测试",
            "market": "A-share",
            "initial_capital": -1000
        },
        expected_status=422
    )

    # 8.3 枚举值不合法
    test_api(
        "market值不合法",
        "/api/v1/account/create",
        {
            "account_name": "测试",
            "market": "invalid"
        },
        expected_status=422
    )

def test_auth_cases():
    """测试认证"""
    print_section("9. 认证测试")

    # 9.1 无token
    test_api(
        "无认证token",
        "/api/v1/account/query",
        {"page": 1, "page_size": 20},
        expected_status=401,
        skip_auth=True
    )

    # 9.2 错误token
    test_api(
        "错误的token",
        "/api/v1/account/query",
        {"page": 1, "page_size": 20},
        expected_status=401,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid-token"
        }
    )

def print_summary():
    """打印测试总结"""
    print_section("测试总结")

    total = test_results["passed"] + test_results["failed"]
    passed_rate = (test_results["passed"] / total * 100) if total > 0 else 0

    print(f"""
总测试数: {total}
✅ 通过: {test_results["passed"]}
❌ 失败: {test_results["failed"]}
通过率: {passed_rate:.1f}%
""")

    if test_results["errors"]:
        print("\n失败的测试详情:")
        print("-" * 70)
        for i, error in enumerate(test_results["errors"], 1):
            print(f"\n{i}. {error['name']}")
            print(f"   端点: {error.get('endpoint', 'N/A')}")
            if 'expected' in error:
                print(f"   预期: {error['expected']}, 实际: {error['actual']}")
            if 'error' in error:
                print(f"   错误: {error['error']}")
            if 'response' in error:
                print(f"   响应: {error['response']}")

    return test_results["failed"] == 0

def main():
    """主函数"""
    print("="*70)
    print("  AI投资管理系统 - 全接口测试")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)

    # 0. 健康检查
    if not test_backend_health():
        sys.exit(1)

    # 1. 账户管理
    test_account_apis()

    # 2. 持仓管理
    test_holding_apis()

    # 3. 交易记录
    test_trade_apis()

    # 4. 股票数据
    test_stock_apis()

    # 5. AI分析
    test_ai_apis()

    # 6. 事件管理
    test_event_apis()

    # 7. 用户接口
    test_user_apis()

    # 8. 参数验证
    test_validation_cases()

    # 9. 认证测试
    test_auth_cases()

    # 总结
    success = print_summary()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
