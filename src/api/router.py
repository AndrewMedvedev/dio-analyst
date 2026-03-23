import json
from datetime import UTC, datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, status

from ..agents import chatbot, rag
from ..agents.subagents import agent_aio
from ..agents.subagents.utils import parce_site_markups
from ..agents.workflow import agent
from ..core.schemas import Chat, Role

router = APIRouter(prefix="/api/v1")


@router.get("/seo", status_code=status.HTTP_200_OK)
async def get_seo(url: str, user_id: str) -> dict:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    result = await agent.ainvoke({"url": url})  # type: ignore  # noqa: PGH003
    del result["html"]
    del result["markdown"]
    await rag.indexing(
        text=json.dumps(result),
        metadata={
            "tenant_id": user_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )
    return result


@router.get("/aio", status_code=status.HTTP_200_OK)
async def get_aio(url: str, user_id: str) -> dict:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    markdown, html = await parce_site_markups(url)
    result = await agent_aio.ainvoke({"url": url, "html": html, "markdown": markdown})  # type: ignore  # noqa: PGH003
    del result["html"]
    del result["markdown"]
    await rag.indexing(
        text=json.dumps(result),
        metadata={
            "tenant_id": user_id,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )
    return result


@router.post("/chat", status_code=status.HTTP_200_OK)
async def answer(chat: Chat) -> Chat:
    result = await chatbot.call_chatbot(user_id=chat.user_id, user_prompt=chat.text)
    return Chat(user_id=chat.user_id, role=Role.AI, text=result)


@router.get("/least/visited", status_code=status.HTTP_200_OK)
async def get_least_visited() -> dict:
    today = datetime.now(UTC).date()
    one_month_ago = today - relativedelta(months=1)

    return {}
