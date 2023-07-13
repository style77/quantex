from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from quantex.web.api.router import api_router
from quantex.web.lifetime import (
    register_shutdown_event,
    register_startup_event,
)
from quantex.web.middlewares import ProcessTimeHeader, SecurityHeaders


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="insightguard",
        version=metadata.version("insightguard"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    app.add_middleware(ProcessTimeHeader)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeaders)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
