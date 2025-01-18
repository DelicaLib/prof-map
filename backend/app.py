import uvicorn
from fastapi import FastAPI, APIRouter
from dependency_injector.wiring import Provide, inject

from lifespan import lifespan
from routers.debug import debug_router
from routers.language_model import language_model
from routers.openai import openai_router
from routers.parser import parser_router
from routers.vacancy import vacancy_router

from fastapi.middleware.cors import CORSMiddleware

main_router = APIRouter(prefix="/api/v1")

origins = [
    "http://127.0.0.1:5500",  # Ваш фронтенд
    "http://localhost:5500",  # Альтернативный адрес
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Road MAP",
        lifespan=lifespan
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Разрешенные источники
        allow_credentials=True,  # Если нужны cookies
        allow_methods=["*"],  # Разрешенные методы (GET, POST и т.д.)
        allow_headers=["*"],  # Разрешенные заголовки
    )
    return app


@inject
def prepare_app(app: FastAPI = Provide["fastapi_app"]):
    main_router.include_router(debug_router)
    main_router.include_router(language_model)
    main_router.include_router(parser_router)
    main_router.include_router(openai_router)
    main_router.include_router(vacancy_router)

    app.include_router(main_router)


@inject
def run(app: FastAPI = Provide["fastapi_app"], port: int | None = None):
    uvicorn.run(app, host="0.0.0.0", port=port)
