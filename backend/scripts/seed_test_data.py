"""
测试数据导入脚本

基于真实的青岛啤酒持仓数据创建测试数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.holding import Holding
from app.models.stock import Stock
from app.models.trade import Trade
from app.models.event import Event
from app.models.ai_decision import AIDecision
from sqlalchemy import select
from datetime import datetime, timedelta
from decimal import Decimal


async def seed_data():
    """导入测试数据"""
    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("开始导入测试数据...")
        print("=" * 70)

        # 1. 获取testuser
        result = await db.execute(
            select(User).where(User.username == "testuser")
        )
        user = result.scalar_one_or_none()

        if not user:
            print("❌ 未找到testuser，请先注册该用户")
            return

        print(f"\n✅ 找到用户: {user.username} (ID: {user.user_id})")

        # 2. 创建A股账户
        print("\n[1] 创建账户...")
        result = await db.execute(
            select(Account).where(
                Account.user_id == user.user_id,
                Account.account_name == "我的A股账户"
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            account = Account(
                user_id=user.user_id,
                account_name="我的A股账户",
                broker="华泰证券",
                account_number="8888****1234",
                market="A股",
                status="active",
                total_value=Decimal("105280.00"),  # 基于持仓市值
                available_cash=Decimal("50000.00"),
                created_at=datetime.utcnow() - timedelta(days=180)
            )
            db.add(account)
            await db.flush()
            print(f"    ✅ 创建账户: {account.account_name} (ID: {account.account_id})")
        else:
            print(f"    ⚠️  账户已存在: {account.account_name} (ID: {account.account_id})")

        # 3. 创建股票信息（青岛啤酒）
        print("\n[2] 创建股票信息...")
        result = await db.execute(
            select(Stock).where(Stock.symbol == "600600")
        )
        stock = result.scalar_one_or_none()

        if not stock:
            stock = Stock(
                symbol="600600",
                name="青岛啤酒",
                market="A股",
                industry="食品饮料",
                sector="啤酒",
                list_date=datetime(1993, 7, 15).date(),
                pinyin="QDPJ"
            )
            db.add(stock)
            await db.flush()
            print(f"    ✅ 创建股票: {stock.name} ({stock.symbol})")
        else:
            print(f"    ⚠️  股票已存在: {stock.name} ({stock.symbol})")

        # 4. 创建持仓（青岛啤酒）
        print("\n[3] 创建持仓...")
        result = await db.execute(
            select(Holding).where(
                Holding.user_id == user.user_id,
                Holding.account_id == account.account_id,
                Holding.symbol == "600600"
            )
        )
        holding = result.scalar_one_or_none()

        if not holding:
            holding = Holding(
                user_id=user.user_id,
                account_id=account.account_id,
                symbol="600600",
                stock_name="青岛啤酒",
                quantity=Decimal("1600"),  # 真实持仓
                average_cost=Decimal("78.406"),  # 真实成本价
                current_price=Decimal("65.80"),  # 当前价
                market_value=Decimal("105280.00"),  # 1600 * 65.80
                cost_basis=Decimal("125449.60"),  # 1600 * 78.406
                profit_loss=Decimal("-20169.60"),  # 105280 - 125449.60
                profit_loss_percent=Decimal("-16.08"),
                position_ratio=Decimal("67.73"),  # 105280 / 155280 * 100
                created_at=datetime.utcnow() - timedelta(days=120),
                updated_at=datetime.utcnow()
            )
            db.add(holding)
            print(f"    ✅ 创建持仓: {holding.stock_name} - 1600股")
            print(f"       成本: ¥78.406  当前: ¥65.80  亏损: ¥-20,169.60 (-16.08%)")
        else:
            print(f"    ⚠️  持仓已存在: {holding.stock_name}")

        # 5. 创建交易记录
        print("\n[4] 创建交易记录...")
        result = await db.execute(
            select(Trade).where(
                Trade.user_id == user.user_id,
                Trade.account_id == account.account_id,
                Trade.symbol == "600600"
            )
        )
        existing_trades = result.scalars().all()

        if not existing_trades:
            # 第一笔买入（800股 @ 76.50）
            trade1 = Trade(
                user_id=user.user_id,
                account_id=account.account_id,
                symbol="600600",
                stock_name="青岛啤酒",
                trade_type="buy",
                quantity=Decimal("800"),
                price=Decimal("76.50"),
                amount=Decimal("61200.00"),  # 800 * 76.50
                commission=Decimal("18.36"),  # 万3
                tax=Decimal("0"),
                total_fees=Decimal("18.36"),
                trade_date=datetime.utcnow() - timedelta(days=120),
                trade_time=datetime.utcnow() - timedelta(days=120),
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=120)
            )

            # 第二笔买入（800股 @ 80.312）
            trade2 = Trade(
                user_id=user.user_id,
                account_id=account.account_id,
                symbol="600600",
                stock_name="青岛啤酒",
                trade_type="buy",
                quantity=Decimal("800"),
                price=Decimal("80.312"),
                amount=Decimal("64249.60"),  # 800 * 80.312
                commission=Decimal("19.27"),
                tax=Decimal("0"),
                total_fees=Decimal("19.27"),
                trade_date=datetime.utcnow() - timedelta(days=90),
                trade_time=datetime.utcnow() - timedelta(days=90),
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=90)
            )

            db.add(trade1)
            db.add(trade2)
            print(f"    ✅ 创建交易记录:")
            print(f"       - 买入 800股 @ ¥76.50 (120天前)")
            print(f"       - 买入 800股 @ ¥80.312 (90天前)")
            print(f"       平均成本: ¥78.406")
        else:
            print(f"    ⚠️  交易记录已存在 ({len(existing_trades)}笔)")

        # 6. 创建事件
        print("\n[6] 创建相关事件...")
        result = await db.execute(
            select(Event).where(
                Event.symbol == "600600",
                Event.title.like("%啤酒%")
            )
        )
        existing_events = result.scalars().all()

        if not existing_events:
            event = Event(
                user_id=user.user_id,
                symbol="600600",
                stock_name="青岛啤酒",
                event_category="industry",
                event_subcategory="industry_trends",
                title="啤酒行业进入消费旺季，高端化趋势明显",
                summary="随着气温回升和节假日临近，啤酒行业进入传统消费旺季。行业龙头加大高端产品布局，盈利能力有望提升。",
                content="近期啤酒行业数据显示，高端啤酒销售占比持续提升，行业龙头如青岛啤酒、华润啤酒等公司高端产品销售增长迅速...",
                source_url="https://example.com/news/beer-industry-trends",
                importance="high",
                impact_direction="positive",
                impact_score=Decimal("75.0"),
                event_date=datetime.utcnow() - timedelta(days=3),
                published_at=datetime.utcnow() - timedelta(days=3),
                created_at=datetime.utcnow() - timedelta(days=3)
            )
            db.add(event)
            print(f"    ✅ 创建事件: 啤酒行业进入消费旺季")
        else:
            print(f"    ⚠️  事件已存在")

        # 提交所有更改
        await db.commit()

        print("\n" + "=" * 70)
        print("✅ 测试数据导入完成！")
        print("=" * 70)
        print("\n📊 数据摘要:")
        print(f"  - 用户: testuser (ID: {user.user_id})")
        print(f"  - 账户: {account.account_name} (ID: {account.account_id})")
        print(f"  - 持仓: 青岛啤酒 1600股")
        print(f"  - 成本: ¥78.406")
        print(f"  - 当前: ¥65.80")
        print(f"  - 盈亏: ¥-20,169.60 (-16.08%)")
        print("\n🌐 现在可以登录前端查看真实数据:")
        print("  http://localhost:5175/login")
        print("  账号: testuser / Test123456")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(seed_data())
