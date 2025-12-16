"""
Common Schemas

统一响应格式和通用数据结构
"""

from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """
    统一API响应格式

    成功响应:
    {
        "code": 0,
        "message": "success",
        "data": {...}
    }

    失败响应:
    {
        "code": 1001,
        "message": "无权访问该资源",
        "data": null
    }
    """

    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "Response":
        """
        创建成功响应

        Args:
            data: 响应数据
            message: 响应消息

        Returns:
            Response对象
        """
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None) -> "Response":
        """
        创建错误响应

        Args:
            code: 错误码
            message: 错误消息
            data: 错误详情数据（可选）

        Returns:
            Response对象
        """
        return cls(code=code, message=message, data=data)

    class Config:
        json_schema_extra = {"example": {"code": 0, "message": "success", "data": {}}}


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = 1
    page_size: int = 20

    class Config:
        json_schema_extra = {"example": {"page": 1, "page_size": 20}}


class PaginationResponse(BaseModel, Generic[T]):
    """
    分页响应数据结构

    {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
    """

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginationResponse[T]":
        """
        创建分页响应

        Args:
            items: 数据列表
            total: 总数
            page: 当前页码
            page_size: 每页数量

        Returns:
            PaginationResponse对象
        """
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)

    class Config:
        json_schema_extra = {"example": {"items": [], "total": 100, "page": 1, "page_size": 20, "total_pages": 5}}


class ErrorDetail(BaseModel):
    """错误详情"""

    field: Optional[str] = None
    message: str

    class Config:
        json_schema_extra = {"example": {"field": "email", "message": "邮箱格式不正确"}}
