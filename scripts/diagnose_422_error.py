#!/usr/bin/env python3
"""
API 422错误诊断脚本

帮助诊断和解决 POST /api/v1/account/create 的422错误
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
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
        print("  或")
        print("  cd backend && uvicorn app.main:app --reload")
        return False

def test_auth():
    """测试认证"""
    print_section("2. 认证测试")

    # 测试1: 无token
    print("\n测试1: 无认证token")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/account/query",
            json={"page": 1, "page_size": 10},
            timeout=5
        )
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {e}")

    # 测试2: 错误token
    print("\n测试2: 错误的token")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/account/query",
            json={"page": 1, "page_size": 10},
            headers={"Authorization": "Bearer invalid-token"},
            timeout=5
        )
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"  错误: {e}")

    # 测试3: 开发token
    print("\n测试3: 开发环境token (dev-token)")
    print("  说明: 开发环境可能自动创建用户")

def test_account_create_validation():
    """测试账户创建的各种验证情况"""
    print_section("3. 账户创建参数验证")

    test_cases = [
        {
            "name": "缺少必填字段 account_name",
            "data": {
                "market": "A-share"
            },
            "expected": "422错误 - 缺少account_name"
        },
        {
            "name": "缺少必填字段 market",
            "data": {
                "account_name": "测试账户"
            },
            "expected": "422错误 - 缺少market"
        },
        {
            "name": "market值不合法",
            "data": {
                "account_name": "测试账户",
                "market": "invalid-market"
            },
            "expected": "422错误 - market必须是A-share/HK/US"
        },
        {
            "name": "initial_capital为负数",
            "data": {
                "account_name": "测试账户",
                "market": "A-share",
                "initial_capital": -1000
            },
            "expected": "422错误 - 初始资金不能为负"
        },
        {
            "name": "正确的最小参数",
            "data": {
                "account_name": f"测试账户_{datetime.now().strftime('%H%M%S')}",
                "market": "A-share"
            },
            "expected": "200成功"
        },
        {
            "name": "正确的完整参数",
            "data": {
                "account_name": f"完整测试_{datetime.now().strftime('%H%M%S')}",
                "market": "A-share",
                "broker": "测试券商",
                "account_number": "1234567890",
                "initial_capital": 100000.0
            },
            "expected": "200成功"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"  预期结果: {test_case['expected']}")
        print(f"  请求数据: {json.dumps(test_case['data'], ensure_ascii=False)}")

        try:
            # 这里不带认证,会返回401
            response = requests.post(
                f"{BASE_URL}/api/v1/account/create",
                json=test_case['data'],
                timeout=5
            )
            print(f"  状态码: {response.status_code}")

            if response.status_code == 422:
                error_detail = response.json()
                print(f"  422错误详情:")
                if 'detail' in error_detail:
                    if isinstance(error_detail['detail'], list):
                        for err in error_detail['detail']:
                            print(f"    - 字段: {err.get('loc', [])}")
                            print(f"      错误: {err.get('msg', '')}")
                            print(f"      类型: {err.get('type', '')}")
                    else:
                        print(f"    {error_detail['detail']}")
            else:
                print(f"  响应: {response.json()}")

        except Exception as e:
            print(f"  请求异常: {e}")

def print_solutions():
    """打印解决方案"""
    print_section("4. 常见422错误及解决方案")

    solutions = [
        {
            "error": "422 Unprocessable Entity - 缺少account_name",
            "cause": "请求体中没有account_name字段",
            "solution": "确保请求中包含 'account_name': '账户名称'"
        },
        {
            "error": "422 Unprocessable Entity - 缺少market",
            "cause": "请求体中没有market字段",
            "solution": "确保请求中包含 'market': 'A-share' (或HK/US)"
        },
        {
            "error": "422 Unprocessable Entity - field required",
            "cause": "必填字段缺失",
            "solution": "检查API文档,补全所有必填字段"
        },
        {
            "error": "422 Unprocessable Entity - value is not a valid enumeration member",
            "cause": "枚举值不合法(如market)",
            "solution": "market必须是: 'A-share', 'HK', 或 'US'"
        },
        {
            "error": "422 Unprocessable Entity - ensure this value is greater than or equal to 0",
            "cause": "数值字段为负数(如initial_capital)",
            "solution": "initial_capital必须 >= 0"
        }
    ]

    for i, sol in enumerate(solutions, 1):
        print(f"\n{i}. {sol['error']}")
        print(f"   原因: {sol['cause']}")
        print(f"   解决: {sol['solution']}")

def print_correct_example():
    """打印正确示例"""
    print_section("5. 正确的请求示例")

    print("\n前端代码示例 (TypeScript):")
    print("""
```typescript
// 最小参数
const response = await post('/account/create', {
  account_name: '我的A股账户',
  market: 'A-share'
})

// 完整参数
const response = await post('/account/create', {
  account_name: '我的A股账户',
  market: 'A-share',
  broker: '华泰证券',
  account_number: '1234567890',
  initial_capital: 100000.0
})
```
""")

    print("\ncURL示例:")
    print("""
```bash
curl -X POST http://localhost:8000/api/v1/account/create \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer your-token" \\
  -d '{
    "account_name": "我的A股账户",
    "market": "A-share",
    "broker": "华泰证券",
    "initial_capital": 100000.0
  }'
```
""")

def check_backend_logs():
    """检查后端日志"""
    print_section("6. 后端日志检查")

    print("\n如果以上测试都无法解决问题,请检查后端日志:")
    print("\n方法1: 查看dev.sh启动的日志")
    print("  tail -f scripts/logs/backend.log")

    print("\n方法2: 如果手动启动后端,查看终端输出")
    print("  后端会显示详细的请求和错误信息")

    print("\n方法3: 启用调试模式")
    print("  在backend/.env中设置:")
    print("  LOG_LEVEL=DEBUG")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  API 422错误诊断工具")
    print("  目标: POST /api/v1/account/create")
    print("="*60)

    # 1. 健康检查
    if not test_health():
        return

    # 2. 认证测试
    test_auth()

    # 3. 参数验证测试
    test_account_create_validation()

    # 4. 解决方案
    print_solutions()

    # 5. 正确示例
    print_correct_example()

    # 6. 日志检查
    check_backend_logs()

    # 总结
    print_section("总结")
    print("""
422错误通常是以下原因之一:

1. ❌ 缺少必填字段 (account_name, market)
   → 检查请求体,补全必填字段

2. ❌ 字段类型错误 (如initial_capital不是数字)
   → 检查字段类型,确保符合API文档

3. ❌ 枚举值不合法 (如market='invalid')
   → market只能是: A-share, HK, US

4. ❌ 数值范围错误 (如initial_capital < 0)
   → 初始资金不能为负数

5. ❌ 字符串长度超限 (如account_name > 100字符)
   → 账户名称最长100字符

如果仍无法解决,请:
1. 检查后端日志: tail -f scripts/logs/backend.log
2. 查看API文档: http://localhost:8000/docs
3. 使用Swagger UI测试: http://localhost:8000/docs#/账户管理/create_account_account_create_post
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n诊断已取消")
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
