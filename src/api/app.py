from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..agents.rag import INDEX_NAME, client, delete_old_data
from ..core.errors import AppError
from .routers import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    client.get_or_create_collection(INDEX_NAME)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        delete_old_data,
        trigger="interval",
        hours=1,
        args=[3],
        misfire_grace_time=300,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    setup_middleware(app)
    app.include_router(router)
    return app


def set_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    def value_exception_handler(request: Request, exc: ValueError) -> JSONResponse:  # noqa: ARG001
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc),
                    "status": status.HTTP_400_BAD_REQUEST,
                    "details": {},
                }
            },
        )

    @app.exception_handler(AppError)
    def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:  # noqa: ARG001
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.public_message,
                    "status": exc.status_code,
                    "details": exc.details,
                }
            },
        )


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
