from fastapi import APIRouter, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from ..agents.aio_agent.agent import agent_aio
from ..agents.pipeline_seo import agent_seo

router = APIRouter(prefix="/api/v1")


@router.get("/agent", status_code=status.HTTP_200_OK)
async def answer(url: str) -> dict:
    """Добавляет https:// если протокол не указан"""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    aio = await agent_aio.ainvoke({"url": url})
    seo = await agent_seo.ainvoke({"url": url})
    total_tokens = aio["total_tokens"] + seo["total_tokens"]
    total_money = total_tokens / 1000 * 0.5
    return {
        "seo": seo["result"],
        "json_ld": aio["json_ld"],
        "robots_txt": aio["robots_txt"],
        "llms_txt": aio["llms_txt"],
        "total_tokens": total_tokens,
        "total_money": round(total_money, 2),
    }


def create_fastapi_app() -> FastAPI:
    app = FastAPI()
    setup_middleware(app)
    app.include_router(router)
    return app


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
