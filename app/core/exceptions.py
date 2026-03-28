"""Business exception definitions."""
from typing import Optional


class BusinessException(Exception):
    """业务异常基类。

    所有业务逻辑异常应继承此类，用于全局异常处理器统一处理。
    """

    code: str = "BUSINESS_ERROR"
    message: str = "业务处理失败"
    http_status: int = 400

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        http_status: Optional[int] = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.http_status = http_status or self.http_status
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源未找到异常。"""

    code = "NOT_FOUND"
    message = "资源未找到"
    http_status = 404


class UnauthorizedException(BusinessException):
    """未授权异常。"""

    code = "UNAUTHORIZED"
    message = "未授权访问"
    http_status = 401


class ForbiddenException(BusinessException):
    """禁止访问异常。"""

    code = "FORBIDDEN"
    message = "禁止访问"
    http_status = 403


class ValidationException(BusinessException):
    """数据校验异常。"""

    code = "VALIDATION_ERROR"
    message = "数据校验失败"
    http_status = 400


class AuthenticationException(BusinessException):
    """认证失败异常。"""

    code = "AUTH_FAILED"
    message = "认证失败"
    http_status = 401


class CodeExpiredException(BusinessException):
    """验证码过期异常。"""

    code = "CODE_EXPIRED"
    message = "验证码已过期"
    http_status = 400


class CodeUsedException(BusinessException):
    """验证码已使用异常。"""

    code = "CODE_USED"
    message = "验证码已使用"
    http_status = 400


class CodeInvalidException(BusinessException):
    """验证码无效异常。"""

    code = "CODE_INVALID"
    message = "验证码错误"
    http_status = 400