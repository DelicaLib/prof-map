import uvicorn
from fastapi import FastAPI, APIRouter
from dependency_injector.wiring import Provide, inject

from lifespan import lifespan
from routers.debug import debug_router

main_router = APIRouter(prefix="/api/v1")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Road MAP",
        lifespan=lifespan
    )
    return app


@inject
def prepare_app(app: FastAPI = Provide["fastapi_app"]):
    main_router.include_router(debug_router)
    app.include_router(main_router)


@inject
def run(app: FastAPI = Provide["fastapi_app"], port: int | None = None):
    uvicorn.run(app, port=port)
