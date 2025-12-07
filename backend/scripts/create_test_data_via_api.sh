#!/bin/bash

# 通过API创建测试数据

BASE_URL="http://localhost:8000/api/v1"

# 首先登录获取token
echo "==================================================================="
echo "Step 1: 登录获取token"
echo "==================================================================="

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=Test123456")

echo "$LOGIN_RESPONSE" | python3 -m json.tool

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败，无法获取token"
    exit 1
fi

echo "✅ 成功获取token"

# 创建A股账户
echo ""
echo "==================================================================="
echo "Step 2: 创建A股账户"
echo "==================================================================="

ACCOUNT_RESPONSE=$(curl -s -X POST "$BASE_URL/account/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_name": "我的A股账户",
    "broker": "华泰证券",
    "account_number": "8888****1234",
    "market": "A股"
  }')

echo "$ACCOUNT_RESPONSE" | python3 -m json.tool

ACCOUNT_ID=$(echo "$ACCOUNT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('account_id', 0))" 2>/dev/null)

if [ "$ACCOUNT_ID" = "0" ]; then
    echo "⚠️  账户可能已存在，尝试查询现有账户"

    QUERY_RESPONSE=$(curl -s -X POST "$BASE_URL/account/query" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{}')

    ACCOUNT_ID=$(echo "$QUERY_RESPONSE" | python3 -c "import sys, json; items=json.load(sys.stdin).get('data', {}).get('items', []); print(items[0]['account_id'] if items else 0)" 2>/dev/null)
fi

echo "✅ 账户ID: $ACCOUNT_ID"

# 创建交易记录（买入青岛啤酒）
echo ""
echo "==================================================================="
echo "Step 3: 创建交易记录 - 第一笔买入"
echo "==================================================================="

TRADE1_RESPONSE=$(curl -s -X POST "$BASE_URL/trade/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": '$ACCOUNT_ID',
    "symbol": "600600",
    "stock_name": "青岛啤酒",
    "trade_type": "buy",
    "quantity": 800,
    "price": 76.50,
    "trade_time": "2024-08-20 10:30:00",
    "commission": 18.36,
    "notes": "首次建仓"
  }')

echo "$TRADE1_RESPONSE" | python3 -m json.tool

echo ""
echo "==================================================================="
echo "Step 4: 创建交易记录 - 第二笔买入"
echo "==================================================================="

TRADE2_RESPONSE=$(curl -s -X POST "$BASE_URL/trade/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": '$ACCOUNT_ID',
    "symbol": "600600",
    "stock_name": "青岛啤酒",
    "trade_type": "buy",
    "quantity": 800,
    "price": 80.312,
    "trade_time": "2024-09-20 14:15:00",
    "commission": 19.27,
    "notes": "加仓"
  }')

echo "$TRADE2_RESPONSE" | python3 -m json.tool

# 同步持仓
echo ""
echo "==================================================================="
echo "Step 5: 同步持仓数据"
echo "==================================================================="

SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/holding/sync" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": '$ACCOUNT_ID'
  }')

echo "$SYNC_RESPONSE" | python3 -m json.tool

echo ""
echo "==================================================================="
echo "✅ 测试数据创建完成！"
echo "==================================================================="
echo ""
echo "现在可以登录前端查看数据："
echo "  http://localhost:5175/login"
echo "  账号: testuser / Test123456"
echo ""
echo "账户ID: $ACCOUNT_ID"
echo "持仓: 青岛啤酒 1600股 (800@76.50 + 800@80.312)"
echo "平均成本: ¥78.406"
echo "==================================================================="
