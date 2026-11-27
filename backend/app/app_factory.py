import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import setup_logging
from app.core.rate_limit import rate_limit_middleware
from app.core.responses import response_error


def create_app(routers) -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-Id"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    @app.middleware("http")
    async def enforce_rate_limit(request: Request, call_next):
        return await rate_limit_middleware(request, call_next)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        meta = {"request_id": request.state.request_id}
        return JSONResponse(
            status_code=exc.status_code,
            content=response_error(exc.code, exc.message, exc.details, meta),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        meta = {"request_id": request.state.request_id}
        details = [
            {"loc": list(err.get("loc", [])), "msg": err.get("msg"), "type": err.get("type")}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=response_error("VALIDATION_ERROR", "Invalid input", details, meta),
        )

    for r in routers:
        if getattr(r, "no_prefix", False):
            app.include_router(r)
        else:
            app.include_router(r, prefix=settings.api_prefix)

    return app
