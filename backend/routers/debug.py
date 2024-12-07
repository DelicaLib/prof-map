from fastapi import APIRouter

debug_router = APIRouter(prefix="/debug", tags=["debug"])


@debug_router.get("/ping")
async def read_items() -> str:
    return "OK"
