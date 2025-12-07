"""
Custom Exceptions

统一异常体系 - 定义业务异常和错误码
"""

from typing import Any, Optional


class APIException(Exception):
    """
    API异常基类

    所有业务异常继承此类
    """
    code: int = 1000
    message: str = "服务器内部错误"
    data: Optional[Any] = None

    def __init__(self, message: Optional[str] = None, data: Optional[Any] = None):
        if message:
            self.message = message
        if data:
            self.data = data
        super().__init__(self.message)


class BusinessException(APIException):
    """业务异常 (通用业务错误)"""
    code = 1000
    message = "业务处理失败"


class PermissionDenied(APIException):
    """权限异常 (无权访问)"""
    code = 1001
    message = "无权访问该资源"


class ResourceNotFound(APIException):
    """资源不存在异常"""
    code = 1002
    message = "资源不存在"


class ValidationError(APIException):
    """验证错误异常"""
    code = 1003
    message = "数据验证失败"


class DuplicateError(APIException):
    """重复数据异常"""
    code = 1004
    message = "数据已存在"


class AuthenticationError(APIException):
    """认证失败异常"""
    code = 1005
    message = "认证失败"


class InvalidOperation(APIException):
    """非法操作异常"""
    code = 1006
    message = "操作不允许"


class ExternalServiceError(APIException):
    """外部服务错误异常"""
    code = 1007
    message = "外部服务调用失败"


class RateLimitExceeded(APIException):
    """频率限制异常"""
    code = 1008
    message = "请求过于频繁"


class DataIntegrityError(APIException):
    """数据完整性错误"""
    code = 1009
    message = "数据完整性校验失败"


# 具体业务异常示例

class AccountException(BusinessException):
    """账户相关异常"""
    pass


class AccountNotFound(ResourceNotFound):
    """账户不存在"""
    message = "账户不存在"


class AccountAccessDenied(PermissionDenied):
    """无权访问该账户"""
    message = "无权访问该账户"


class AccountNameDuplicate(DuplicateError):
    """账户名称重复"""
    message = "账户名称已存在"


class TradeException(BusinessException):
    """交易相关异常"""
    pass


class TradeNotFound(ResourceNotFound):
    """交易记录不存在"""
    message = "交易记录不存在"


class InvalidTradeData(ValidationError):
    """无效的交易数据"""
    message = "交易数据不合法"


class StockException(BusinessException):
    """股票相关异常"""
    pass


class StockNotFound(ResourceNotFound):
    """股票不存在"""
    message = "股票不存在"


class HoldingException(BusinessException):
    """持仓相关异常"""
    pass


class InsufficientHolding(InvalidOperation):
    """持仓数量不足"""
    message = "持仓数量不足"


class EventException(BusinessException):
    """事件相关异常"""
    pass


class EventNotFound(ResourceNotFound):
    """事件不存在"""
    message = "事件不存在"
