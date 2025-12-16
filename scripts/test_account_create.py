#!/usr/bin/env python3
"""
账户创建接口测试脚本

测试 POST /api/v1/account/create 的各种场景
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 开发环境Token（需要在backend/.env中设置 DEV_MODE=true）
DEV_TOKEN = "dev-token"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_backend_health():
    """测试后端健康状态"""
    print_section("1. 后端健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 后端状态: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 后端无法访问: {e}")
        print("\n请先启动后端:")
        print("  ./scripts/dev.sh")
        return False

def test_create_account(test_name, data, headers, expected_status=200):
    """
    测试账户创建

    Args:
        test_name: 测试名称
        data: 请求数据
        headers: 请求头
        expected_status: 预期状态码
    """
    print(f"\n测试: {test_name}")
    print(f"  请求数据: {json.dumps(data, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/account/create",
            json=data,
            headers=headers,
            timeout=10
        )

        print(f"  状态码: {response.status_code}")

        if response.status_code == expected_status:
            print(f"  ✅ 符合预期 (期望{expected_status})")
        else:
            print(f"  ❌ 不符合预期 (期望{expected_status}, 实际{response.status_code})")

        # 打印响应
        try:
            response_data = response.json()
            print(f"  响应:")
            print(f"    {json.dumps(response_data, ensure_ascii=False, indent=4)}")

            # 如果是422错误，详细打印验证错误
            if response.status_code == 422 and 'detail' in response_data:
                print(f"\n  📋 验证错误详情:")
                if isinstance(response_data['detail'], list):
                    for err in response_data['detail']:
                        print(f"    • 字段: {' -> '.join(str(x) for x in err.get('loc', []))}")
                        print(f"      错误: {err.get('msg', '')}")
                        print(f"      类型: {err.get('type', '')}")
                else:
                    print(f"    {response_data['detail']}")

            return response_data
        except:
            print(f"  响应文本: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return None

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  账户创建接口测试")
    print("  目标: POST /api/v1/account/create")
    print("="*60)

    # 1. 健康检查
    if not test_backend_health():
        return

    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEV_TOKEN}"
    }

    print_section("2. 认证测试")

    # 测试1: 无token
    test_create_account(
        "无认证token",
        {"account_name": "测试", "market": "A-share"},
        {"Content-Type": "application/json"},
        expected_status=401
    )

    print_section("3. 参数验证测试")

    # 测试2: 缺少account_name
    test_create_account(
        "缺少必填字段 account_name",
        {"market": "A-share"},
        headers,
        expected_status=422
    )

    # 测试3: 缺少market
    test_create_account(
        "缺少必填字段 market",
        {"account_name": "测试账户"},
        headers,
        expected_status=422
    )

    # 测试4: market值不合法
    test_create_account(
        "market值不合法",
        {"account_name": "测试账户", "market": "invalid-market"},
        headers,
        expected_status=422
    )

    # 测试5: initial_capital为负数
    test_create_account(
        "initial_capital为负数",
        {
            "account_name": "测试账户",
            "market": "A-share",
            "initial_capital": -1000
        },
        headers,
        expected_status=422
    )

    # 测试6: account_name过长
    test_create_account(
        "account_name超过100字符",
        {
            "account_name": "测" * 101,
            "market": "A-share"
        },
        headers,
        expected_status=422
    )

    print_section("4. 正常创建测试")

    timestamp = datetime.now().strftime('%H%M%S')

    # 测试7: 最小参数（不提供broker和account_number）
    result1 = test_create_account(
        "✅ 最小参数（不提供broker和account_number）",
        {
            "account_name": f"最小参数测试_{timestamp}",
            "market": "A-share"
        },
        headers,
        expected_status=200
    )

    # 测试8: 完整参数
    result2 = test_create_account(
        "✅ 完整参数",
        {
            "account_name": f"完整参数测试_{timestamp}",
            "market": "A-share",
            "broker": "华泰证券",
            "account_number": "1234567890",
            "initial_capital": 100000.0
        },
        headers,
        expected_status=200
    )

    # 测试9: broker和account_number为空字符串
    result3 = test_create_account(
        "✅ broker和account_number为空字符串",
        {
            "account_name": f"空字符串测试_{timestamp}",
            "market": "HK",
            "broker": "",
            "account_number": ""
        },
        headers,
        expected_status=200
    )

    # 测试10: 不同市场类型
    for market in ["A-share", "HK", "US"]:
        test_create_account(
            f"✅ 市场类型: {market}",
            {
                "account_name": f"{market}账户_{timestamp}",
                "market": market,
                "initial_capital": 50000
            },
            headers,
            expected_status=200
        )

    print_section("5. 测试总结")

    print("""
测试结论:

✅ 应该通过的测试:
  1. 最小参数（只提供account_name和market）
  2. 完整参数（提供所有字段）
  3. broker和account_number为空字符串
  4. 不同市场类型（A-share/HK/US）

❌ 应该拒绝的测试:
  1. 无认证token (401)
  2. 缺少account_name (422)
  3. 缺少market (422)
  4. market值不合法 (422)
  5. initial_capital为负数 (422)
  6. account_name超过100字符 (422)

🔧 修复验证:
  如果测试7-10都返回200状态码，说明422错误已修复！
  broker和account_number现在可以为NULL或空字符串。

📚 相关文档:
  • 问题诊断: docs/troubleshooting/422-error-account-create.md
  • API文档: http://localhost:8000/docs
  • 数据库迁移: backend/alembic/versions/d064a2ea4323_*.py
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
