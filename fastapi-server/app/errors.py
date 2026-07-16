"""统一错误码体系——所有 API 响应格式为 {code, message, data}。"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# ─── 错误码表 ────────────────────────────────────────────────────

class ErrorCode:
    """错误码常量。"""

    # 通用
    SUCCESS = 0
    UNKNOWN = 10000
    VALIDATION_ERROR = 10001

    # 认证 10xxx
    UNAUTHORIZED = 10010
    INVALID_TOKEN = 10011
    TOKEN_EXPIRED = 10012
    FORBIDDEN = 10020
    ADMIN_REQUIRED = 10021

    # 资源 20xxx
    NOT_FOUND = 20000
    USER_NOT_FOUND = 20001
    CASE_NOT_FOUND = 20002

    # 业务 30xxx
    RATE_LIMITED = 30001
    FREE_TIER_EXHAUSTED = 30002
    FILE_TOO_LARGE = 30010
    FILE_TYPE_DENIED = 30011
    AI_SERVICE_ERROR = 30020
    PDF_GENERATION_FAILED = 30030

    # 输入 40xxx
    INVALID_INPUT = 40000
    INVALID_UUID = 40001
    MESSAGE_TOO_LONG = 40002

    # 服务 50xxx
    SERVER_ERROR = 50000


# HTTP 状态码 → 错误码映射
_HTTP_TO_CODE = {
    400: ErrorCode.INVALID_INPUT,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    413: ErrorCode.FILE_TOO_LARGE,
    415: ErrorCode.FILE_TYPE_DENIED,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    500: ErrorCode.SERVER_ERROR,
}


# ─── 响应构建 ─────────────────────────────────────────────────────

def success_response(data=None, message: str = "ok") -> dict:
    """构建成功响应。"""
    return {"code": ErrorCode.SUCCESS, "message": message, "data": data}


def error_response(code: int, message: str, data=None, status_code: int = 400) -> JSONResponse:
    """构建错误响应。"""
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": data},
    )


# ─── 全局异常处理器 ────────────────────────────────────────────────


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """统一处理 HTTPException，返回 {code, message, data}。"""
    code = _HTTP_TO_CODE.get(exc.status_code, ErrorCode.UNKNOWN)
    return error_response(code, exc.detail, status_code=exc.status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """统一处理 Pydantic 校验错误。"""
    errors = exc.errors()
    detail = errors[0].get("msg", "输入校验失败") if errors else "输入校验失败"
    return error_response(ErrorCode.VALIDATION_ERROR, detail, status_code=422)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未预期的异常。"""
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("未处理的异常: %s", exc)
    return error_response(ErrorCode.SERVER_ERROR, "服务器内部错误", status_code=500)
