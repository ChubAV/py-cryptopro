from typing import Any, Callable
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import uuid


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, api_key: str, exclude_paths: list[str] = None):
        super().__init__(app)
        self.api_key = api_key
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != self.api_key:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return await call_next(request)


class UUIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, request_id):
        super().__init__(app)
        self.request_id = request_id

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        self.request_id.set(str(uuid.uuid4()))
        response = await call_next(request)
        return response
