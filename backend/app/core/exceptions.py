from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    """Base application exception for TRACEBACK backend."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        title: str = "Internal Server Error",
        detail: str = "An unexpected error occurred on the server.",
        instance: Optional[str] = None,
        type_: str = "about:blank",
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.instance = instance
        self.type_ = type_


class ResourceNotFoundException(AppException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=f"{resource} with identifier '{identifier}' was not found.",
            type_="https://traceback.dev/errors/not-found",
        )


class BadRequestException(AppException):
    """Exception raised for invalid client requests."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=detail,
            type_="https://traceback.dev/errors/bad-request",
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """HTTP Exception handler returning RFC-7807 compliant problem details."""
    payload = {
        "type": exc.type_,
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
        "instance": exc.instance or str(request.url),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)
