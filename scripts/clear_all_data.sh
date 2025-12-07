#!/bin/bash
# 清空所有业务数据脚本

echo "🗑️  清空所有业务数据..."
echo ""

psql -U investment_user -d investment_db << EOF
-- 清空所有业务数据（按外键依赖顺序）

-- 1. 清空持仓数据
DELETE FROM holdings;

-- 2. 清空交易记录
DELETE FROM trades;

-- 3. 清空事件数据
DELETE FROM events;

-- 4. 清空股票评价
DELETE FROM user_stock_reviews;

-- 5. 清空AI对话
DELETE FROM ai_conversations;

-- 6. 清空AI决策
DELETE FROM ai_decisions;

-- 7. 清空账户数据
DELETE FROM accounts;

-- 8. 清空股票数据
DELETE FROM stocks;

-- 9. 清空测试用户
DELETE FROM users WHERE username LIKE 'testuser_%';

-- 统计剩余数据
SELECT '=== 数据清空完成 ===' as status;
SELECT
    '用户数: ' || (SELECT COUNT(*) FROM users) ||
    ' | 账户数: ' || (SELECT COUNT(*) FROM accounts) ||
    ' | 持仓数: ' || (SELECT COUNT(*) FROM holdings) ||
    ' | 交易数: ' || (SELECT COUNT(*) FROM trades) as summary
UNION ALL
SELECT
    '事件数: ' || (SELECT COUNT(*) FROM events) ||
    ' | 评价数: ' || (SELECT COUNT(*) FROM user_stock_reviews) ||
    ' | AI决策: ' || (SELECT COUNT(*) FROM ai_decisions) as summary;
EOF

echo ""
echo "✅ 所有业务数据已清空，可以开始测试"
