import json
import logging
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from . import rag
from .subagents import agent_aio, agent_analyst, agent_importer, agent_seo

logger = logging.getLogger(__name__)


class State(TypedDict):
    url: str
    importer_result: dict
    analyst_result: dict
    aio_result: dict
    seo_result: dict
    rag_result: str
    total_tokens: int
    total_money: float


async def get_importer_result(state: State) -> dict:
    result = await agent_importer.ainvoke({"url": state["url"], "max_result": 3})  # type: ignore  # noqa: PGH003
    return {"importer_result": result}


async def get_analyst_result(state: State) -> dict:
    result = await agent_analyst.ainvoke({"url": state["url"]})  # type: ignore  # noqa: PGH003
    logger.info(result)
    total_money = (result["total_tokens"] / 1000) * 0.41
    total_tokens = result["total_tokens"]
    del result["url"]
    del result["markdown_main_page"]
    del result["total_tokens"]
    return {
        "analyst_result": result,
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


async def get_aio_result(state: State) -> dict:
    result = await agent_aio.ainvoke(
        {
            "url": state["url"],
            "markdown": state["importer_result"]["markdown"],  # type: ignore  # noqa: PGH003
            "html": state["importer_result"]["html"],  # type: ignore  # noqa: PGH003
        }  # type: ignore  # noqa: PGH003
    )  # type: ignore  # noqa: PGH003
    logger.info(result)
    total_tokens = state["total_tokens"] + result["total_tokens"]
    money = (result["total_tokens"] / 1000) * 0.41
    total_money = money + state["total_money"]
    del result["url"]
    del result["markdown"]
    del result["html"]
    del result["total_tokens"]
    return {"aio_result": result, "total_tokens": total_tokens, "total_money": total_money}


async def get_seo_result(state: State) -> dict:
    result = await agent_seo.ainvoke(
        {
            "url": state["url"],
            "markdown": state["importer_result"]["markdown"],  # type: ignore  # noqa: PGH003
            "html": state["importer_result"]["html"],  # type: ignore  # noqa: PGH003
        }
    )  # type: ignore  # noqa: PGH003
    logger.info(result)
    total_tokens = state["total_tokens"] + result["total_tokens"]
    money = (result["total_tokens"] / 1000) * 0.41
    total_money = money + state["total_money"]
    return {
        "seo_result": result["result"],
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


async def save_in_rag(state: State) -> dict:
    result = state.copy()
    result["importer_result"] = {}
    rag.indexing(
        text=json.dumps(result), metadata={"tenant_id": "b77f7b87-2d40-45fa-b653-2ff34d5fd587"}
    )
    return {"rag_result": "saved"}


builder = StateGraph(State)

builder.add_node("get_importer_result", get_importer_result)
builder.add_node("get_analyst_result", get_analyst_result)
builder.add_node("get_aio_result", get_aio_result)
builder.add_node("get_seo_result", get_seo_result)
builder.add_node("save_in_rag", save_in_rag)
builder.add_edge(START, "get_importer_result")
builder.add_edge("get_importer_result", "get_analyst_result")
builder.add_edge("get_analyst_result", "get_aio_result")
builder.add_edge("get_aio_result", "get_seo_result")
builder.add_edge("get_seo_result", "save_in_rag")
builder.add_edge("save_in_rag", END)
agent = builder.compile()
