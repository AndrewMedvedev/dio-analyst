import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from .subagents import agent_analyst, agent_content_generation, agent_seo
from .subagents.utils import parce_site_markups


class State(TypedDict):
    url: str
    html: str
    markdown: list[str]
    analyst_result: dict
    seo_result: dict
    content_generation_result: dict
    total_tokens: Annotated[int, operator.add]
    total_money: Annotated[float, operator.add]


async def get_site_markups(state: State) -> dict:
    markdown, html = await parce_site_markups(state["url"])  # type: ignore  # noqa: PGH003
    return {"markdown": markdown, "html": html}


async def get_analyst_result(state: State) -> dict:
    result = await agent_analyst.ainvoke({"url": state["url"], "markdown": state["markdown"]})  # type: ignore  # noqa: PGH003
    total_tokens = result["total_tokens"] + state.get("total_tokens", 0)
    total_money = result["total_money"] + state.get("total_money", 0)

    del result["url"]
    del result["markdown"]
    del result["total_tokens"]
    del result["total_money"]
    return {
        "analyst_result": result,
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


async def get_seo_result(state: State) -> dict:
    result = await agent_seo.ainvoke(
        {
            "url": state["url"],
            "markdown": state["markdown"],
            "html": state["html"],
        }  # type: ignore  # noqa: PGH003
    )
    total_tokens = result["total_tokens"] + state.get("total_tokens", 0)
    total_money = result["total_money"] + state.get("total_money", 0)
    del result["total_tokens"]
    del result["total_money"]
    return {
        "seo_result": result["result"],
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


async def get_content_generation_result(state: State) -> dict:
    result = await agent_content_generation.ainvoke(
        {"url": state["url"], "html": state["html"], "markdown": state["markdown"]}  # type: ignore  # noqa: PGH003
    )
    total_tokens = result["total_tokens"] + state.get("total_tokens", 0)
    total_money = result["total_money"] + state.get("total_money", 0)
    del result["html"]
    del result["markdown"]
    del result["total_tokens"]
    del result["total_money"]
    return {
        "content_generation_result": result,
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


builder = StateGraph(State)

builder.add_node("get_site_markups", get_site_markups)
builder.add_node("get_analyst_result", get_analyst_result)
builder.add_node("get_seo_result", get_seo_result)
builder.add_node("get_content_generation_result", get_content_generation_result)

builder.add_edge(START, "get_site_markups")

builder.add_edge("get_site_markups", "get_analyst_result")
builder.add_edge("get_site_markups", "get_seo_result")
builder.add_edge("get_site_markups", "get_content_generation_result")

builder.add_edge("get_analyst_result", END)
builder.add_edge("get_seo_result", END)
builder.add_edge("get_content_generation_result", END)

agent = builder.compile()
