from __future__ import annotations

from typing import Iterable, Optional
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .routers.health import router as _health_router


def create_app(
    *,
    title: str = "SoftAPI Starter",
    version: str = "0.2.2",
    include_default_routes: bool = True,
    routers: Optional[Iterable[APIRouter]] = None,
    cors_origins: Optional[Iterable[str]] = None,
    docs_url: Optional[str] = "/docs",
    redoc_url: Optional[str] = "/redoc",
    openapi_url: Optional[str] = "/openapi.json",
) -> FastAPI:
    """
    Create a ready-to-run FastAPI app with sensible defaults.

    Parameters
    ----------
    title : str
        OpenAPI title.
    version : str
        OpenAPI version string (also shown on /docs).
    include_default_routes : bool
        If True, mounts GET /health and GET /__version__.
    routers : Iterable[APIRouter] | None
        Additional routers to include.
    cors_origins : Iterable[str] | None
        If provided, enables CORS for these origins.
    docs_url, redoc_url, openapi_url : str | None
        Set to None to disable.

    Returns
    -------
    FastAPI
    """
    app = FastAPI(title=title, version=version,
                  docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url)

    # CORS
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(cors_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Default lightweight routes
    if include_default_routes:
        app.include_router(_health_router, tags=["__softapi"])

    # User-provided routers
    if routers:
        for r in routers:
            app.include_router(r)

    return app


__all__ = ["create_app"]
