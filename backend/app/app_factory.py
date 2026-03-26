import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.responses import response_error
from app.core.errors import AppError
from app.core.cache import get_redis
from app.core.security import decode_token

logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _rate_limit(request: Request) -> JSONResponse | None:
    r = get_redis()
    if not r:
        return None
    ip = _client_ip(request)
    user_id = None
    auth = request.headers.get("authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            if payload.get("type") == "access":
                user_id = payload.get("sub")
        except Exception:
            user_id = None

    try:
        pipe = r.pipeline()
        ip_key = f"rl:ip:{ip}"
        pipe.incr(ip_key, 1)
        pipe.expire(ip_key, 60)
        if user_id:
            user_key = f"rl:user:{user_id}"
            pipe.incr(user_key, 1)
            pipe.expire(user_key, 60)
        results = pipe.execute()
        ip_count = results[0]
        user_count = results[2] if user_id else 0
        if ip_count > settings.rate_limit_ip_per_min:
            return JSONResponse(
                status_code=429,
                content=response_error("RATE_LIMIT", "Too many requests", [], {"request_id": request.state.request_id}),
            )
        if user_id and user_count > settings.rate_limit_user_per_min:
            return JSONResponse(
                status_code=429,
                content=response_error("RATE_LIMIT", "Too many requests", [], {"request_id": request.state.request_id}),
            )
    except Exception as exc:
        logger.warning("Rate limit error: %s", exc)

    return None


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
        allow_headers=["*"]
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        rl_response = _rate_limit(request)
        if rl_response:
            return rl_response
        response = await call_next(request)
        response.headers["X-Request-Id"] = request.state.request_id
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        meta = {"request_id": request.state.request_id}
        return JSONResponse(status_code=exc.status_code, content=response_error(exc.code, exc.message, exc.details, meta))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        meta = {"request_id": request.state.request_id}
        return JSONResponse(status_code=400, content=response_error("VALIDATION_ERROR", "Invalid input", exc.errors(), meta))

    for r in routers:
        app.include_router(r, prefix=settings.api_prefix)

    return app
