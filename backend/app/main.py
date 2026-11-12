"""FastAPI application entrypoint — paper trading only."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import health
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import configure_logging, get_logger
from app.core.security import assert_paper_only

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    assert_paper_only(settings)
    logger.info(
        "Application starting",
        extra={
            "extra_fields": {
                "event": "startup",
                "app_mode": settings.app_mode,
                "live_trading_enabled": False,
            }
        },
    )
    yield
    logger.info("Application stopped", extra={"extra_fields": {"event": "shutdown"}})


def create_app() -> FastAPI:
    settings = get_settings()
    assert_paper_only(settings)

    application = FastAPI(
        title="Trading Bot API",
        description=(
            "API pessoal de análise e paper trading (BTC/ETH Spot). "
            "PAPER TRADING — SEM DINHEIRO REAL. Sem endpoints de ordens reais."
        ),
        version=__version__,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    application.add_exception_handler(Exception, unhandled_error_handler)

    application.include_router(health.router, prefix="/api/v1")

    return application


app = create_app()
