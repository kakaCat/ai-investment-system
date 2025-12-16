"""
AI Daily Analysis Service

AI每日批量分析业务服务 - Service + Converter + Builder
"""

import uuid
from typing import List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.ai_decision_repo import AIDecisionRepository
from app.repositories.stock_repo import StockRepository
from app.utils.ai_client import ai_client, AIPromptBuilder
from app.utils.tushare_client import tushare_client


class DailyAnalysisService:
    """
    AI每日批量分析业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.ai_decision_repo = AIDecisionRepository()
        self.stock_repo = StockRepository()

    async def create_task(self, db: AsyncSession, user_id: int, stock_symbols: List[str]) -> dict:
        """
        创建并执行批量分析任务（简化版，同步执行）

        Args:
            db: 数据库会话
            user_id: 用户ID
            stock_symbols: 股票代码列表

        Returns:
            任务信息
        """
        # 1. 生成任务ID
        task_id = str(uuid.uuid4())

        # 2. 验证和限制
        if not stock_symbols:
            raise ValueError("股票列表不能为空")
        if len(stock_symbols) > 20:
            raise ValueError("单次最多分析20只股票")

        # 3. 批量分析股票（简化版：顺序执行）
        results = []
        for symbol in stock_symbols:
            try:
                # 查询股票信息
                stock = await self.stock_repo.get_by_symbol(db, symbol)
                stock_name = stock.name if stock else symbol

                # 调用AI分析
                analysis_result = await DailyAnalysisConverter.analyze_stock(symbol=symbol, stock_name=stock_name)

                # 保存结果
                decision_data = {
                    "user_id": user_id,
                    "symbol": symbol,
                    "stock_name": stock_name,
                    "analysis_type": "daily",
                    "ai_score": analysis_result.get("ai_score", {}),
                    "ai_suggestion": analysis_result.get("ai_suggestion", ""),
                    "ai_strategy": analysis_result.get("ai_strategy", {}),
                    "ai_reasons": analysis_result.get("ai_reasons", []),
                    "confidence_level": Decimal(str(analysis_result.get("confidence_level", 50.0))),
                }

                decision = await self.ai_decision_repo.create(db, decision_data)
                results.append(decision)

            except Exception as e:
                print(f"分析{symbol}失败: {e}")
                # 继续处理下一只股票

        await db.commit()

        # 4. 构建响应
        return DailyAnalysisBuilder.build_task_response(
            task_id=task_id,
            total_stocks=len(stock_symbols),
            processed_stocks=len(results),
            results=[DailyAnalysisConverter.convert_single_decision(d) for d in results],
        )

    async def get_results(self, db: AsyncSession, user_id: int, task_id: str) -> dict:
        """
        获取批量分析结果

        Args:
            db: 数据库会话
            user_id: 用户ID
            task_id: 任务ID

        Returns:
            分析结果
        """
        # 查询最近的daily类型分析结果
        decisions, total = await self.ai_decision_repo.query_by_user(
            db=db, user_id=user_id, analysis_type="daily", page=1, page_size=100
        )

        # 转换数据
        decision_data = [DailyAnalysisConverter.convert_single_decision(d) for d in decisions]

        # 构建响应
        return DailyAnalysisBuilder.build_results_response(task_id=task_id, decisions=decision_data, total_count=total)


class DailyAnalysisConverter:
    """
    AI每日批量分析转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    async def analyze_stock(symbol: str, stock_name: str) -> dict:
        """
        分析单只股票

        Args:
            symbol: 股票代码
            stock_name: 股票名称

        Returns:
            分析结果
        """
        # 1. 获取真实股票数据
        stock_data = await DailyAnalysisConverter.fetch_stock_data(symbol)

        # 2. 构建Prompt（包含真实数据）
        messages = AIPromptBuilder.build_stock_analysis_prompt(
            symbol=symbol,
            stock_name=stock_name,
            stock_data=stock_data,  # ✅ 传入真实数据
            include_fundamentals=True,
            include_technicals=True,
            include_valuation=True,
        )

        # 3. 调用AI
        ai_response = await ai_client.chat_completion(messages=messages, temperature=0.7, max_tokens=1500)

        # 4. 解析响应
        try:
            analysis_result = DailyAnalysisConverter._parse_ai_response(ai_response)
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            analysis_result = DailyAnalysisConverter._get_default_analysis(symbol, stock_name)

        return analysis_result

    @staticmethod
    async def fetch_stock_data(symbol: str) -> dict:
        """
        获取真实股票数据（简化版，用于批量分析）

        Args:
            symbol: 股票代码

        Returns:
            股票数据字典
        """
        stock_data = {}

        try:
            # 只获取关键数据，减少API调用
            quote = await tushare_client.get_realtime_quote(symbol)
            if quote:
                stock_data["quote"] = quote

            fundamentals = await tushare_client.get_fundamentals(symbol)
            if fundamentals:
                stock_data["fundamentals"] = fundamentals

        except Exception as e:
            print(f"获取{symbol}数据失败: {e}")

        return stock_data

    @staticmethod
    def _parse_ai_response(ai_response: str) -> dict:
        """解析AI响应为结构化数据"""
        import json

        response = ai_response.strip()

        # 移除markdown代码块
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        # 提取JSON
        if "{" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            result = json.loads(json_str)

            # 验证必需字段
            if all(k in result for k in ["ai_score", "ai_suggestion", "confidence_level"]):
                return result

        raise ValueError("无法解析AI响应")

    @staticmethod
    def _get_default_analysis(symbol: str, stock_name: str) -> dict:
        """获取默认分析结果"""
        return {
            "ai_score": {"fundamental_score": 70, "technical_score": 65, "valuation_score": 75, "overall_score": 70},
            "ai_suggestion": f"建议关注{stock_name}",
            "ai_strategy": {
                "target_price": 0.0,
                "recommended_position": 5.0,
                "risk_level": "medium",
                "holding_period": "观察期",
                "stop_loss_price": 0.0,
            },
            "ai_reasons": ["数据不足，建议持续关注"],
            "confidence_level": 50.0,
        }

    @staticmethod
    def convert_single_decision(decision) -> dict:
        """转换单个AI决策"""
        return {
            "decision_id": decision.decision_id,
            "symbol": decision.symbol,
            "stock_name": decision.stock_name,
            "ai_score": decision.ai_score,
            "ai_suggestion": decision.ai_suggestion,
            "ai_strategy": decision.ai_strategy,
            "ai_reasons": decision.ai_reasons or [],
            "confidence_level": float(decision.confidence_level) if decision.confidence_level else None,
            "created_at": decision.created_at.isoformat() if decision.created_at else None,
        }


class DailyAnalysisBuilder:
    """
    AI每日批量分析构建器（静态类）

    职责：构建响应数据结构
    """

    @staticmethod
    def build_task_response(task_id: str, total_stocks: int, processed_stocks: int, results: List[dict]) -> dict:
        """构建任务创建响应"""
        return {
            "task_id": task_id,
            "status": "completed" if processed_stocks == total_stocks else "partial",
            "total_stocks": total_stocks,
            "processed_stocks": processed_stocks,
            "results": results,
            "created_at": datetime.now().isoformat(),
        }

    @staticmethod
    def build_results_response(task_id: str, decisions: List[dict], total_count: int) -> dict:
        """构建分析结果响应"""
        return {
            "task_id": task_id,
            "status": "completed",
            "total_count": total_count,
            "results": decisions,
            "total_tokens_used": len(decisions) * 1200,  # 估算
            "completed_at": datetime.now().isoformat(),
        }
