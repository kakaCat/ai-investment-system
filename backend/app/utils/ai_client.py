"""
AI Client - 统一AI调用接口

支持多种AI后端：
1. 本地模型（Ollama）- 默认，免费
2. DeepSeek API - 配置API Key后可用
"""

import json
import httpx
from typing import List, Dict, Optional
from app.core.config import settings


class AIClient:
    """
    AI客户端统一接口

    自动选择可用的AI后端：
    1. 优先本地Ollama（如果运行中）
    2. 备选DeepSeek API（如果配置了API Key）
    """

    def __init__(self):
        self.local_url = "http://localhost:11434"  # Ollama默认端口
        self.deepseek_url = settings.DEEPSEEK_API_URL
        self.deepseek_key = settings.DEEPSEEK_API_KEY
        self.timeout = 120.0  # AI调用超时时间

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        model: Optional[str] = None,
    ) -> str:
        """
        聊天补全接口

        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]
            temperature: 温度参数（0-1）
            max_tokens: 最大token数
            model: 指定模型（可选）

        Returns:
            AI回复内容

        Raises:
            Exception: AI调用失败
        """
        # 1. 尝试本地Ollama
        try:
            response = await self._call_ollama(messages, temperature, max_tokens, model)
            if response:
                return response
        except Exception as e:
            print(f"Ollama调用失败: {e}")

        # 2. 尝试DeepSeek API
        if self.deepseek_key:
            try:
                response = await self._call_deepseek(messages, temperature, max_tokens, model)
                if response:
                    return response
            except Exception as e:
                print(f"DeepSeek调用失败: {e}")
                raise Exception(f"DeepSeek API调用失败: {e}")

        # 3. 如果都不可用，返回Mock数据（开发阶段）
        return self._generate_mock_response(messages)

    async def _call_ollama(
        self, messages: List[Dict[str, str]], temperature: float, max_tokens: int, model: Optional[str] = None
    ) -> Optional[str]:
        """
        调用本地Ollama

        需要先安装并运行Ollama:
        1. 安装: curl -fsSL https://ollama.com/install.sh | sh
        2. 运行模型: ollama run qwen2.5:7b
        """
        if not model:
            model = "qwen2:latest"  # 默认使用Qwen2（系统已安装）

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 检查Ollama是否运行
            try:
                health_check = await client.get(f"{self.local_url}/api/tags")
                if health_check.status_code != 200:
                    return None
            except Exception:
                return None

            # 转换消息格式为Ollama格式
            prompt = self._messages_to_prompt(messages)

            # 调用Ollama API
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }

            response = await client.post(f"{self.local_url}/api/generate", json=payload)

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")

            return None

    async def _call_deepseek(
        self, messages: List[Dict[str, str]], temperature: float, max_tokens: int, model: Optional[str] = None
    ) -> Optional[str]:
        """
        调用DeepSeek API

        需要先配置环境变量:
        DEEPSEEK_API_KEY=your_api_key
        """
        if not self.deepseek_key:
            return None

        if not model:
            model = settings.DEEPSEEK_MODEL

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}

            payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

            response = await client.post(f"{self.deepseek_url}/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = response.text
                raise Exception(f"DeepSeek API错误 (状态码: {response.status_code}): {error_msg}")

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        将消息列表转换为单个prompt（用于Ollama）
        """
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"系统: {content}\n")
            elif role == "user":
                prompt_parts.append(f"用户: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"助手: {content}\n")

        prompt_parts.append("助手: ")
        return "\n".join(prompt_parts)

    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """
        生成Mock响应（开发阶段使用）
        """
        last_message = messages[-1]["content"] if messages else ""

        return f"""[Mock AI响应 - 请配置本地模型或DeepSeek API]

您的问题: {last_message[:100]}...

这是一个模拟的AI响应。要获得真实的AI分析，请：

方式1: 本地模型（推荐，免费）
1. 安装Ollama: curl -fsSL https://ollama.com/install.sh | sh
2. 运行模型: ollama run qwen2.5:7b
3. 重启后端服务

方式2: DeepSeek API
1. 获取API Key: https://platform.deepseek.com
2. 配置环境变量: DEEPSEEK_API_KEY=your_key
3. 重启后端服务
"""


class AIPromptBuilder:
    """
    AI Prompt构建器

    职责：构建各种场景的结构化Prompt
    """

    @staticmethod
    def build_stock_analysis_prompt(
        symbol: str,
        stock_name: str,
        stock_data: Optional[Dict] = None,
        include_fundamentals: bool = True,
        include_technicals: bool = True,
        include_valuation: bool = True,
    ) -> List[Dict[str, str]]:
        """
        构建单股分析Prompt

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            stock_data: 股票数据（可选）
            include_fundamentals: 包含基本面分析
            include_technicals: 包含技术面分析
            include_valuation: 包含估值分析

        Returns:
            消息列表
        """
        system_prompt = """你是一位专业的投资分析师，擅长股票分析和投资建议。

请按照以下JSON格式返回分析结果：

{
  "ai_score": {
    "fundamental_score": 75,
    "technical_score": 68,
    "valuation_score": 82,
    "overall_score": 75
  },
  "ai_suggestion": "建议持有，中长期看好",
  "ai_strategy": {
    "target_price": 120.0,
    "recommended_position": 15.0,
    "risk_level": "medium",
    "holding_period": "6-12个月",
    "stop_loss_price": 85.0
  },
  "ai_reasons": [
    "理由1",
    "理由2",
    "理由3"
  ],
  "confidence_level": 78.5
}

评分标准：
- fundamental_score: 基本面评分（0-100）
- technical_score: 技术面评分（0-100）
- valuation_score: 估值评分（0-100）
- overall_score: 综合评分（0-100）
- confidence_level: 置信度（0-100）

风险等级：low/medium/high
"""

        # 构建用户问题
        analysis_types = []
        if include_fundamentals:
            analysis_types.append("基本面")
        if include_technicals:
            analysis_types.append("技术面")
        if include_valuation:
            analysis_types.append("估值")

        user_prompt = f"""请分析股票：{stock_name}（{symbol}）

分析维度：{', '.join(analysis_types)}

"""

        # 添加股票数据（如果有）
        if stock_data:
            user_prompt += "**当前股票数据**:\n\n"

            # 1. 实时行情数据
            if "quote" in stock_data:
                quote = stock_data["quote"]
                user_prompt += f"""**实时行情**:
- 最新价: {quote.get('current_price', 'N/A')} 元
- 涨跌幅: {quote.get('change_percent', 'N/A')}%
- 涨跌额: {quote.get('change_amount', 'N/A')} 元
- 今开: {quote.get('open_price', 'N/A')} 元
- 最高: {quote.get('high_price', 'N/A')} 元
- 最低: {quote.get('low_price', 'N/A')} 元
- 昨收: {quote.get('close_price', 'N/A')} 元
- 成交量: {quote.get('volume', 'N/A')} 股
- 成交额: {quote.get('amount', 'N/A') / 100000000:.2f if quote.get('amount') else 'N/A'} 亿元
- 数据来源: {quote.get('data_source', 'unknown')}

"""

            # 2. 基本面数据
            if "fundamentals" in stock_data:
                fundamentals = stock_data["fundamentals"]
                total_market_cap_val = fundamentals.get("total_market_cap")
                total_market_cap_str = f"{total_market_cap_val / 10000:.2f}" if total_market_cap_val else "N/A"
                circulating_market_cap_val = fundamentals.get("circulating_market_cap")
                circulating_market_cap_str = (
                    f"{circulating_market_cap_val / 10000:.2f}" if circulating_market_cap_val else "N/A"
                )

                user_prompt += f"""**基本面指标**:
- 市盈率(PE): {fundamentals.get('pe_ratio', 'N/A')}
- 市净率(PB): {fundamentals.get('pb_ratio', 'N/A')}
- 市销率(PS): {fundamentals.get('ps_ratio', 'N/A')}
- 总市值: {total_market_cap_str} 亿元
- 流通市值: {circulating_market_cap_str} 亿元

"""

            # 3. 技术指标
            if "technicals" in stock_data:
                technicals = stock_data["technicals"]
                user_prompt += f"""**技术指标**:
- MA5: {technicals.get('ma5', 'N/A')} 元
- MA10: {technicals.get('ma10', 'N/A')} 元
- MA20: {technicals.get('ma20', 'N/A')} 元
- MA60: {technicals.get('ma60', 'N/A')} 元

"""

            # 4. 股票信息
            if "info" in stock_data:
                info = stock_data["info"]
                user_prompt += f"""**股票信息**:
- 股票名称: {info.get('name', 'N/A')}
- 所属行业: {info.get('industry', 'N/A')}
- 上市板块: {info.get('market', 'N/A')}

"""
        else:
            user_prompt += "**注意**: 暂无实时数据，请基于股票代码和名称进行定性分析。\n\n"

        user_prompt += "请严格按照JSON格式返回分析结果。"

        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    @staticmethod
    def build_chat_prompt(
        user_message: str,
        history: List[Dict[str, str]] = None,
        context_symbol: Optional[str] = None,
        context_data: Optional[Dict] = None,
    ) -> List[Dict[str, str]]:
        """
        构建对话Prompt

        Args:
            user_message: 用户消息
            history: 对话历史
            context_symbol: 上下文股票代码
            context_data: 上下文数据

        Returns:
            消息列表
        """
        system_prompt = """你是一位专业的AI投资顾问，可以回答股票投资相关的问题。

你的能力：
1. 分析股票基本面、技术面、估值
2. 提供投资建议和策略
3. 解释市场事件和影响
4. 回答投资相关问题

请用专业、客观、易懂的语言回答用户问题。
"""

        # 添加上下文信息
        if context_symbol and context_data:
            system_prompt += f"""

当前讨论股票：{context_data.get('stock_name', '')}（{context_symbol}）
相关数据：{json.dumps(context_data, ensure_ascii=False, indent=2)}
"""

        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        if history:
            messages.extend(history[-10:])  # 最多保留最近10轮对话

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages

    @staticmethod
    def build_daily_review_prompt(date: str, holdings: List[Dict], events: List[Dict]) -> List[Dict[str, str]]:
        """
        构建每日复盘Prompt

        Args:
            date: 复盘日期
            holdings: 持仓列表
            events: 事件列表

        Returns:
            消息列表
        """
        system_prompt = """你是一位专业的投资顾问，负责生成每日投资复盘报告。

请按照以下JSON格式返回复盘报告：

{
  "summary": "今日市场概况和主要变化",
  "holdings_analysis": "持仓股票分析",
  "events_impact": "重要事件影响分析",
  "suggestions": [
    "建议1",
    "建议2"
  ],
  "risks": [
    "风险1",
    "风险2"
  ],
  "next_actions": [
    "行动1",
    "行动2"
  ]
}
"""

        # 构建持仓信息
        holdings_info = "\n".join(
            [
                f"- {h.get('stock_name', '')}（{h.get('symbol', '')}）: "
                f"持仓{h.get('quantity', 0)}股，成本{h.get('cost_price', 0)}元"
                for h in holdings[:10]  # 最多显示10个持仓
            ]
        )

        # 构建事件信息
        events_info = "\n".join(
            [f"- {e.get('title', '')}: {e.get('content', '')[:100]}..." for e in events[:5]]  # 最多显示5个事件
        )

        user_prompt = f"""请生成{date}的投资复盘报告：

当前持仓：
{holdings_info}

今日重要事件：
{events_info}

请严格按照JSON格式返回复盘报告。
"""

        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


# 全局AI客户端实例
ai_client = AIClient()
