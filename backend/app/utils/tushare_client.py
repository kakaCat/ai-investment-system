"""
Tushare数据源客户端

提供股票实时行情、基本面数据、技术指标获取功能

依赖:
- tushare (需要 API Token)
- akshare (备选方案，免费)
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal


class TushareClient:
    """
    Tushare数据源客户端

    自动降级机制:
    1. Tushare API (需要Token) - 专业数据源
    2. AkShare (免费) - 备选方案
    3. Mock数据 (降级) - 无数据源时
    """

    def __init__(self):
        self.tushare_token = os.getenv("TUSHARE_TOKEN", "")
        self.use_tushare = False
        self.use_akshare = False

        # 尝试初始化Tushare
        if self.tushare_token:
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                self.pro = ts.pro_api()
                self.use_tushare = True
                print("✅ Tushare API初始化成功")
            except Exception as e:
                print(f"⚠️  Tushare初始化失败: {e}")

        # 尝试初始化AkShare（备选）
        if not self.use_tushare:
            try:
                import akshare
                self.akshare = akshare
                self.use_akshare = True
                print("✅ AkShare初始化成功（备选方案）")
            except Exception as e:
                print(f"⚠️  AkShare初始化失败: {e}")

        if not self.use_tushare and not self.use_akshare:
            print("⚠️  数据源未配置，将使用Mock数据")
            print("   配置Tushare: export TUSHARE_TOKEN=your_token")
            print("   或安装AkShare: pip install akshare")

    async def get_realtime_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时行情数据

        Args:
            symbol: 股票代码（如 600519）

        Returns:
            实时行情数据，包含:
            - current_price: 当前价格
            - open_price: 开盘价
            - high_price: 最高价
            - low_price: 最低价
            - close_price: 收盘价（前一日）
            - volume: 成交量
            - amount: 成交额
            - change_percent: 涨跌幅(%)
            - change_amount: 涨跌额
        """
        if self.use_tushare:
            return await self._get_quote_tushare(symbol)
        elif self.use_akshare:
            return await self._get_quote_akshare(symbol)
        else:
            return self._get_quote_mock(symbol)

    async def get_fundamentals(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取基本面数据

        Args:
            symbol: 股票代码

        Returns:
            基本面数据，包含:
            - pe_ratio: 市盈率
            - pb_ratio: 市净率
            - ps_ratio: 市销率
            - total_market_cap: 总市值
            - circulating_market_cap: 流通市值
            - roe: 净资产收益率
            - gross_profit_margin: 毛利率
            - debt_to_asset_ratio: 资产负债率
        """
        if self.use_tushare:
            return await self._get_fundamentals_tushare(symbol)
        elif self.use_akshare:
            return await self._get_fundamentals_akshare(symbol)
        else:
            return self._get_fundamentals_mock(symbol)

    async def get_technical_indicators(self, symbol: str, period: int = 30) -> Optional[Dict[str, Any]]:
        """
        获取技术指标

        Args:
            symbol: 股票代码
            period: 计算周期（天数）

        Returns:
            技术指标数据，包含:
            - ma5: 5日均线
            - ma10: 10日均线
            - ma20: 20日均线
            - ma60: 60日均线
            - ema12: 12日指数移动平均
            - ema26: 26日指数移动平均
            - macd: MACD指标
            - kdj_k: KDJ-K值
            - kdj_d: KDJ-D值
            - rsi: RSI相对强弱指标
        """
        if self.use_tushare:
            return await self._get_technical_tushare(symbol, period)
        elif self.use_akshare:
            return await self._get_technical_akshare(symbol, period)
        else:
            return self._get_technical_mock(symbol)

    async def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票信息，包含:
            - name: 股票名称
            - industry: 所属行业
            - market: 上市板块
            - list_date: 上市日期
            - total_share: 总股本
            - float_share: 流通股本
        """
        if self.use_tushare:
            return await self._get_stock_info_tushare(symbol)
        elif self.use_akshare:
            return await self._get_stock_info_akshare(symbol)
        else:
            return self._get_stock_info_mock(symbol)

    # ============= Tushare实现 =============

    async def _get_quote_tushare(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取实时行情"""
        try:
            # 转换股票代码格式（600519 → 600519.SH）
            ts_code = self._convert_symbol_to_tushare(symbol)

            # 获取实时行情
            df = self.pro.daily(ts_code=ts_code, trade_date=datetime.now().strftime("%Y%m%d"))

            if df.empty:
                # 如果当天没数据，获取最近一个交易日
                df = self.pro.daily(ts_code=ts_code, limit=1)

            if df.empty:
                return None

            row = df.iloc[0]

            # 计算涨跌幅和涨跌额
            pre_close = float(row.get('pre_close', row.get('close', 0)))
            current = float(row.get('close', 0))
            change_amount = current - pre_close
            change_percent = (change_amount / pre_close * 100) if pre_close > 0 else 0

            return {
                "current_price": float(row.get('close', 0)),
                "open_price": float(row.get('open', 0)),
                "high_price": float(row.get('high', 0)),
                "low_price": float(row.get('low', 0)),
                "close_price": pre_close,
                "volume": int(row.get('vol', 0)) * 100,  # Tushare单位是手（100股）
                "amount": float(row.get('amount', 0)) * 1000,  # Tushare单位是千元
                "change_percent": round(change_percent, 2),
                "change_amount": round(change_amount, 2),
                "trade_date": row.get('trade_date', ''),
                "data_source": "tushare"
            }
        except Exception as e:
            print(f"Tushare获取行情失败: {e}")
            return None

    async def _get_fundamentals_tushare(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取基本面数据"""
        try:
            ts_code = self._convert_symbol_to_tushare(symbol)

            # 获取日线基本指标
            df = self.pro.daily_basic(ts_code=ts_code, limit=1)

            if df.empty:
                return None

            row = df.iloc[0]

            return {
                "pe_ratio": float(row.get('pe', 0)),
                "pb_ratio": float(row.get('pb', 0)),
                "ps_ratio": float(row.get('ps', 0)),
                "total_market_cap": float(row.get('total_mv', 0)),  # 总市值（万元）
                "circulating_market_cap": float(row.get('circ_mv', 0)),  # 流通市值（万元）
                "data_source": "tushare"
            }
        except Exception as e:
            print(f"Tushare获取基本面失败: {e}")
            return None

    async def _get_technical_tushare(self, symbol: str, period: int) -> Dict[str, Any]:
        """使用Tushare获取技术指标（简化版）"""
        try:
            ts_code = self._convert_symbol_to_tushare(symbol)

            # 获取最近N天的行情数据
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=period+30)).strftime("%Y%m%d")

            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

            if df.empty or len(df) < 5:
                return None

            # 计算均线（简单移动平均）
            df = df.sort_values('trade_date')
            closes = df['close'].values

            ma5 = float(closes[-5:].mean()) if len(closes) >= 5 else 0
            ma10 = float(closes[-10:].mean()) if len(closes) >= 10 else 0
            ma20 = float(closes[-20:].mean()) if len(closes) >= 20 else 0
            ma60 = float(closes[-60:].mean()) if len(closes) >= 60 else 0

            return {
                "ma5": round(ma5, 2),
                "ma10": round(ma10, 2),
                "ma20": round(ma20, 2),
                "ma60": round(ma60, 2),
                "data_source": "tushare"
            }
        except Exception as e:
            print(f"Tushare获取技术指标失败: {e}")
            return None

    async def _get_stock_info_tushare(self, symbol: str) -> Dict[str, Any]:
        """使用Tushare获取股票基本信息"""
        try:
            ts_code = self._convert_symbol_to_tushare(symbol)

            # 获取股票基本信息
            df = self.pro.stock_basic(ts_code=ts_code, fields='ts_code,name,industry,market,list_date')

            if df.empty:
                return None

            row = df.iloc[0]

            return {
                "name": row.get('name', ''),
                "industry": row.get('industry', ''),
                "market": row.get('market', ''),
                "list_date": row.get('list_date', ''),
                "data_source": "tushare"
            }
        except Exception as e:
            print(f"Tushare获取股票信息失败: {e}")
            return None

    # ============= AkShare实现 =============

    async def _get_quote_akshare(self, symbol: str) -> Dict[str, Any]:
        """使用AkShare获取实时行情"""
        try:
            # AkShare获取实时行情
            df = self.akshare.stock_zh_a_spot_em()

            # 查找对应股票
            stock_data = df[df['代码'] == symbol]

            if stock_data.empty:
                return None

            row = stock_data.iloc[0]

            return {
                "current_price": float(row.get('最新价', 0)),
                "open_price": float(row.get('今开', 0)),
                "high_price": float(row.get('最高', 0)),
                "low_price": float(row.get('最低', 0)),
                "close_price": float(row.get('昨收', 0)),
                "volume": int(row.get('成交量', 0)),
                "amount": float(row.get('成交额', 0)),
                "change_percent": float(row.get('涨跌幅', 0)),
                "change_amount": float(row.get('涨跌额', 0)),
                "data_source": "akshare"
            }
        except Exception as e:
            print(f"AkShare获取行情失败: {e}")
            return None

    async def _get_fundamentals_akshare(self, symbol: str) -> Dict[str, Any]:
        """使用AkShare获取基本面数据"""
        try:
            # AkShare获取个股信息
            df = self.akshare.stock_individual_info_em(symbol=symbol)

            if df.empty:
                return None

            # 解析数据
            data_dict = dict(zip(df['item'], df['value']))

            return {
                "pe_ratio": float(data_dict.get('市盈率-动态', 0)),
                "pb_ratio": float(data_dict.get('市净率', 0)),
                "total_market_cap": float(data_dict.get('总市值', 0)),
                "circulating_market_cap": float(data_dict.get('流通市值', 0)),
                "data_source": "akshare"
            }
        except Exception as e:
            print(f"AkShare获取基本面失败: {e}")
            return None

    async def _get_technical_akshare(self, symbol: str, period: int) -> Dict[str, Any]:
        """使用AkShare获取技术指标（简化版）"""
        try:
            # AkShare获取历史行情
            df = self.akshare.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")

            if df.empty or len(df) < 5:
                return None

            # 计算均线
            closes = df['收盘'].values

            ma5 = float(closes[-5:].mean()) if len(closes) >= 5 else 0
            ma10 = float(closes[-10:].mean()) if len(closes) >= 10 else 0
            ma20 = float(closes[-20:].mean()) if len(closes) >= 20 else 0
            ma60 = float(closes[-60:].mean()) if len(closes) >= 60 else 0

            return {
                "ma5": round(ma5, 2),
                "ma10": round(ma10, 2),
                "ma20": round(ma20, 2),
                "ma60": round(ma60, 2),
                "data_source": "akshare"
            }
        except Exception as e:
            print(f"AkShare获取技术指标失败: {e}")
            return None

    async def _get_stock_info_akshare(self, symbol: str) -> Dict[str, Any]:
        """使用AkShare获取股票基本信息"""
        try:
            df = self.akshare.stock_individual_info_em(symbol=symbol)

            if df.empty:
                return None

            data_dict = dict(zip(df['item'], df['value']))

            return {
                "name": data_dict.get('股票简称', ''),
                "industry": data_dict.get('行业', ''),
                "market": data_dict.get('上市时间', ''),
                "data_source": "akshare"
            }
        except Exception as e:
            print(f"AkShare获取股票信息失败: {e}")
            return None

    # ============= Mock实现 =============

    def _get_quote_mock(self, symbol: str) -> Dict[str, Any]:
        """Mock实时行情数据"""
        return {
            "current_price": 1650.50,
            "open_price": 1645.00,
            "high_price": 1658.00,
            "low_price": 1642.00,
            "close_price": 1630.00,
            "volume": 15000000,
            "amount": 24750000000.0,
            "change_percent": 1.26,
            "change_amount": 20.50,
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "data_source": "mock",
            "warning": "使用Mock数据，请配置Tushare或安装AkShare"
        }

    def _get_fundamentals_mock(self, symbol: str) -> Dict[str, Any]:
        """Mock基本面数据"""
        return {
            "pe_ratio": 35.2,
            "pb_ratio": 8.5,
            "ps_ratio": 12.3,
            "total_market_cap": 2075000.0,  # 万元
            "circulating_market_cap": 2075000.0,
            "roe": 28.5,
            "gross_profit_margin": 91.2,
            "debt_to_asset_ratio": 15.3,
            "data_source": "mock",
            "warning": "使用Mock数据，请配置Tushare或安装AkShare"
        }

    def _get_technical_mock(self, symbol: str) -> Dict[str, Any]:
        """Mock技术指标"""
        return {
            "ma5": 1640.50,
            "ma10": 1635.20,
            "ma20": 1620.80,
            "ma60": 1595.30,
            "ema12": 1645.00,
            "ema26": 1625.00,
            "macd": 15.5,
            "kdj_k": 72.3,
            "kdj_d": 68.5,
            "rsi": 58.2,
            "data_source": "mock",
            "warning": "使用Mock数据，请配置Tushare或安装AkShare"
        }

    def _get_stock_info_mock(self, symbol: str) -> Dict[str, Any]:
        """Mock股票信息"""
        return {
            "name": "贵州茅台",
            "industry": "白酒",
            "market": "主板",
            "list_date": "20010827",
            "total_share": 1256197200,
            "float_share": 1256197200,
            "data_source": "mock",
            "warning": "使用Mock数据，请配置Tushare或安装AkShare"
        }

    # ============= 工具方法 =============

    def _convert_symbol_to_tushare(self, symbol: str) -> str:
        """
        转换股票代码为Tushare格式

        600519 → 600519.SH (上交所)
        000858 → 000858.SZ (深交所)
        300xxx → 300xxx.SZ (创业板)
        """
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        else:
            return f"{symbol}.SZ"


# 全局单例
tushare_client = TushareClient()
