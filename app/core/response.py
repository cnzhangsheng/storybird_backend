"""Standard API response format."""
from typing import Generic, TypeVar, Optional, Any

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """标准 API 响应格式。

    Attributes:
        code: 业务状态码，0 表示成功，非 0 表示失败
        message: 响应消息
        data: 响应数据
    """

    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success") -> "ApiResponse[T]":
        """创建成功响应。"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Optional[Any] = None) -> "ApiResponse":
        """创建错误响应。"""
        return cls(code=code, message=message, data=data)


class PagedResponse(BaseModel, Generic[T]):
    """分页响应格式。"""

    code: int = 0
    message: str = "success"
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20