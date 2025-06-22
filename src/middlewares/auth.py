from typing import Optional, List, Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


# simple dummy auth mechanism that only checks for the presence of an Authorization header
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, exclude_paths: Optional[List[str]] = None) -> None:
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health"]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        if "authorization" not in request.headers:
            return JSONResponse({"message": "Unauthorized"}, status_code=401)

        return await call_next(request)
