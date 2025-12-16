"""
Single Stock Analysis Service

单股AI分析业务服务 - Service + Converter + Builder
"""

import json
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.ai_decision_repo import AIDecisionRepository
from app.repositories.stock_repo import StockRepository
from app.utils.ai_client import ai_client, AIPromptBuilder
from app.utils.tushare_client import tushare_client


class SingleAnalysisService:
    """
    单股AI分析业务类

    职责：权限校验、编排流程、事务管理
    """

    def __init__(self):
        self.ai_decision_repo = AIDecisionRepository()
        self.stock_repo = StockRepository()

    async def analyze_stock(
        self,
        db: AsyncSession,
        user_id: int,
        symbol: str,
        analysis_type: str = "comprehensive",
        include_fundamentals: bool = True,
        include_technicals: bool = True,
        include_valuation: bool = True,
    ) -> dict:
        """
        分析单只股票

        Args:
            db: 数据库会话
            user_id: 用户ID
            symbol: 股票代码
            analysis_type: 分析类型
            include_fundamentals: 是否包含基本面分析
            include_technicals: 是否包含技术面分析
            include_valuation: 是否包含估值分析

        Returns:
            AI分析结果
        """
        # 1. 查询股票信息
        stock = await self.stock_repo.get_by_symbol(db, symbol)
        stock_name = stock.name if stock else "未知股票"

        # 2. 获取真实股票数据（行情+基本面+技术指标）
        stock_data = await SingleAnalysisConverter.fetch_stock_data(
            symbol=symbol, include_fundamentals=include_fundamentals, include_technicals=include_technicals
        )

        # 3. 调用AI进行分析
        analysis_result = await SingleAnalysisConverter.analyze_with_ai(
            symbol=symbol,
            stock_name=stock_name,
            stock_data=stock_data,  # ✅ 传入真实股票数据
            include_fundamentals=include_fundamentals,
            include_technicals=include_technicals,
            include_valuation=include_valuation,
        )

        # 3. 准备保存到数据库的数据
        decision_data = SingleAnalysisConverter.prepare_decision_data(
            user_id=user_id,
            symbol=symbol,
            stock_name=stock_name,
            analysis_type="single",
            analysis_result=analysis_result,
        )

        # 4. 保存AI决策到数据库
        decision = await self.ai_decision_repo.create(db, decision_data)
        await db.commit()

        # 5. 使用Builder构建响应
        return SingleAnalysisBuilder.build_analysis_response(decision)

    async def get_ai_suggestions(
        self,
        db: AsyncSession,
        user_id: int,
        priority: str = None,
        action: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        获取AI投资建议列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            priority: 优先级筛选（可选）
            action: 操作类型筛选（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            AI建议列表
        """
        # 1. 查询AI决策记录
        decisions, total = await self.ai_decision_repo.query_by_user(
            db=db, user_id=user_id, analysis_type="single", page=page, page_size=page_size
        )

        # 2. 使用Converter过滤和转换数据
        filtered_suggestions = SingleAnalysisConverter.filter_suggestions(
            decisions=decisions, priority=priority, action=action
        )

        # 3. 使用Builder构建响应
        return SingleAnalysisBuilder.build_suggestions_response(
            suggestions=filtered_suggestions, total=total, page=page, page_size=page_size
        )


class SingleAnalysisConverter:
    """
    单股AI分析转换器（静态类）

    职责：业务逻辑计算
    """

    @staticmethod
    async def fetch_stock_data(symbol: str, include_fundamentals: bool = True, include_technicals: bool = True) -> dict:
        """
        获取真实股票数据

        Args:
            symbol: 股票代码
            include_fundamentals: 是否包含基本面数据
            include_technicals: 是否包含技术指标

        Returns:
            股票数据字典，包含:
            - quote: 实时行情
            - fundamentals: 基本面数据
            - technicals: 技术指标
        """
        stock_data = {}

        try:
            # 1. 获取实时行情（必需）
            quote = await tushare_client.get_realtime_quote(symbol)
            if quote:
                stock_data["quote"] = quote

            # 2. 获取基本面数据（可选）
            if include_fundamentals:
                fundamentals = await tushare_client.get_fundamentals(symbol)
                if fundamentals:
                    stock_data["fundamentals"] = fundamentals

            # 3. 获取技术指标（可选）
            if include_technicals:
                technicals = await tushare_client.get_technical_indicators(symbol)
                if technicals:
                    stock_data["technicals"] = technicals

            # 4. 获取股票基本信息
            stock_info = await tushare_client.get_stock_info(symbol)
            if stock_info:
                stock_data["info"] = stock_info

        except Exception as e:
            print(f"获取股票数据失败: {e}")
            # 即使失败，也返回空字典，AI仍可基于代码和名称分析
            return {}

        return stock_data

    @staticmethod
    async def analyze_with_ai(
        symbol: str,
        stock_name: str,
        stock_data: dict = None,
        include_fundamentals: bool = True,
        include_technicals: bool = True,
        include_valuation: bool = True,
    ) -> dict:
        """
        使用AI进行股票分析

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            stock_data: 股票数据（可选）
            include_fundamentals: 包含基本面分析
            include_technicals: 包含技术面分析
            include_valuation: 包含估值分析

        Returns:
            AI分析结果字典
        """
        # 1. 构建Prompt
        messages = AIPromptBuilder.build_stock_analysis_prompt(
            symbol=symbol,
            stock_name=stock_name,
            stock_data=stock_data,
            include_fundamentals=include_fundamentals,
            include_technicals=include_technicals,
            include_valuation=include_valuation,
        )

        # 2. 调用AI
        ai_response = await ai_client.chat_completion(messages=messages, temperature=0.7, max_tokens=2000)

        # 3. 解析AI响应
        try:
            # 尝试从响应中提取JSON
            analysis_result = SingleAnalysisConverter._parse_ai_response(ai_response)
        except Exception as e:
            print(f"AI响应解析失败: {e}")
            # 使用默认分析结果
            analysis_result = SingleAnalysisConverter._get_default_analysis(symbol, stock_name)

        return analysis_result

    @staticmethod
    def _parse_ai_response(ai_response: str) -> dict:
        """
        解析AI响应为结构化数据

        Args:
            ai_response: AI原始响应

        Returns:
            解析后的分析结果
        """
        # 尝试提取JSON部分
        # 处理多种格式：纯JSON、```json```包裹、混合文本
        response = ai_response.strip()

        # 移除markdown代码块标记
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()

        # 查找JSON对象
        if "{" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            result = json.loads(json_str)

            # 验证必需字段
            required_fields = ["ai_score", "ai_suggestion", "confidence_level"]
            if all(field in result for field in required_fields):
                return result

        raise ValueError("无法从AI响应中解析有效的JSON")

    @staticmethod
    def _get_default_analysis(symbol: str, stock_name: str) -> dict:
        """
        获取默认分析结果（AI解析失败时使用）
        """
        return {
            "ai_score": {"fundamental_score": 70, "technical_score": 65, "valuation_score": 75, "overall_score": 70},
            "ai_suggestion": f"建议关注{stock_name}，等待更多信息",
            "ai_strategy": {
                "target_price": 0.0,
                "recommended_position": 5.0,
                "risk_level": "medium",
                "holding_period": "观察期",
                "stop_loss_price": 0.0,
            },
            "ai_reasons": ["分析数据不足，建议持续关注", "等待更多市场信息", "谨慎评估投资风险"],
            "confidence_level": 50.0,
        }

    @staticmethod
    def prepare_decision_data(
        user_id: int, symbol: str, stock_name: str, analysis_type: str, analysis_result: dict
    ) -> dict:
        """
        准备AI决策数据用于保存到数据库

        Args:
            user_id: 用户ID
            symbol: 股票代码
            stock_name: 股票名称
            analysis_type: 分析类型
            analysis_result: AI分析结果

        Returns:
            数据库记录字典
        """
        return {
            "user_id": user_id,
            "symbol": symbol,
            "stock_name": stock_name,
            "analysis_type": analysis_type,
            "ai_score": analysis_result.get("ai_score", {}),
            "ai_suggestion": analysis_result.get("ai_suggestion", ""),
            "ai_strategy": analysis_result.get("ai_strategy", {}),
            "ai_reasons": analysis_result.get("ai_reasons", []),
            "confidence_level": Decimal(str(analysis_result.get("confidence_level", 50.0))),
        }

    @staticmethod
    def filter_suggestions(decisions, priority: str = None, action: str = None) -> list:
        """
        过滤AI建议

        Args:
            decisions: AI决策列表
            priority: 优先级筛选
            action: 操作类型筛选

        Returns:
            过滤后的建议列表
        """
        suggestions = []
        for d in decisions:
            # 从ai_suggestion中提取操作类型
            suggestion_text = d.ai_suggestion.lower() if d.ai_suggestion else ""
            extracted_action = SingleAnalysisConverter._extract_action(suggestion_text)

            # 提取优先级（基于confidence_level）
            extracted_priority = SingleAnalysisConverter._extract_priority(d.confidence_level)

            # 应用筛选
            if priority and extracted_priority != priority:
                continue
            if action and extracted_action != action:
                continue

            suggestions.append(
                {
                    "decision_id": d.decision_id,
                    "symbol": d.symbol,
                    "stock_name": d.stock_name,
                    "action": extracted_action,
                    "priority": extracted_priority,
                    "suggestion": d.ai_suggestion,
                    "ai_score": d.ai_score,
                    "confidence_level": float(d.confidence_level) if d.confidence_level else None,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
            )

        return suggestions

    @staticmethod
    def _extract_action(suggestion_text: str) -> str:
        """从建议文本中提取操作类型"""
        if "买入" in suggestion_text or "建议买" in suggestion_text:
            return "buy"
        elif "卖出" in suggestion_text or "建议卖" in suggestion_text:
            return "sell"
        elif "持有" in suggestion_text:
            return "hold"
        else:
            return "observe"

    @staticmethod
    def _extract_priority(confidence_level) -> str:
        """从置信度提取优先级"""
        if not confidence_level:
            return "low"

        confidence = float(confidence_level)
        if confidence >= 80:
            return "urgent"
        elif confidence >= 60:
            return "medium"
        else:
            return "low"


class SingleAnalysisBuilder:
    """
    单股AI分析构建器（静态类）

    职责：构建响应数据结构
    """

    @staticmethod
    def build_analysis_response(decision) -> dict:
        """
        构建分析结果响应

        Args:
            decision: AIDecision对象

        Returns:
            分析结果响应数据
        """
        return {
            "decision_id": decision.decision_id,
            "user_id": decision.user_id,
            "symbol": decision.symbol,
            "stock_name": decision.stock_name,
            "analysis_type": decision.analysis_type,
            "ai_score": decision.ai_score,
            "ai_suggestion": decision.ai_suggestion,
            "ai_strategy": decision.ai_strategy,
            "ai_reasons": decision.ai_reasons or [],
            "confidence_level": float(decision.confidence_level) if decision.confidence_level else None,
            "created_at": decision.created_at.isoformat() if decision.created_at else None,
            "dimensions_analyzed": ["fundamentals", "technicals"],  # 默认分析维度
            "data_source": "akshare",  # 数据来源
        }

    @staticmethod
    def build_suggestions_response(suggestions: list, total: int, page: int, page_size: int) -> dict:
        """
        构建建议列表响应

        Args:
            suggestions: 建议数据列表
            total: 总数量
            page: 页码
            page_size: 每页数量

        Returns:
            建议列表响应数据
        """
        return {"total": total, "page": page, "page_size": page_size, "suggestions": suggestions}
