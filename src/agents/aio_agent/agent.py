import logging
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ...core.depends import parser_aio_content, yandex_gpt
from ...core.schemas import ListGenerateAIOContent
from ...utils.checkup import get_json_ld, get_llms_data, get_robots_data
from ..prompts import PROMPT_ANALYZE_ROBOTS, PROMPT_GENERATE_AIO_CONTENT
from ..utils import count_tokens, count_tokens_with_ai_message
from .utils import analyze_json_ld, analyze_llms_txt, generate_json_ld, generate_llms_txt

logger = logging.getLogger(__name__)


class State(TypedDict):
    url: str
    markdown: list[dict]
    html: list[dict]
    new_content: list[dict]
    jsons_ld: list[dict]
    robots_txt: str
    llms_txt: str
    total_tokens: int


async def generate_aio_content(state: State) -> dict:
    new_content: list = []
    total_tokens = 0
    chain = yandex_gpt | parser_aio_content
    for data in state["markdown"]:
        request = PROMPT_GENERATE_AIO_CONTENT.format(
            data=data["markdown"], format_instructions=parser_aio_content.get_format_instructions()
        )
        result: ListGenerateAIOContent = await chain.ainvoke(request)
        tokens = await count_tokens(request, result.model_dump_json())
        total_tokens += tokens
        new_content.append({"url": data["url"], "content": result.model_dump()})
    return {"total_tokens": total_tokens, "new_content": new_content}


async def get_lds(state: State) -> dict:
    total_tokens = 0
    jsons_ld = []
    for index, data in enumerate(state["html"]):
        ld = get_json_ld(data["html"])
        if ld != []:
            analyze = await analyze_json_ld(ld)
            jsons_ld.append({"url": data["url"], "json_ld": analyze["json_ld"]})
            total_tokens += analyze["total_tokens"]
        generate = await generate_json_ld(state["markdown"][index]["markdown"])
        jsons_ld.append({"url": data["url"], "json_ld": generate["json_ld"]})
        total_tokens += generate["total_tokens"]
    total_tokens += state["total_tokens"]
    return {"jsons_ld": jsons_ld, "total_tokens": total_tokens}


async def get_robots(state: State) -> dict:
    data = await get_robots_data(state["url"])
    request = PROMPT_ANALYZE_ROBOTS.format(data=data)
    result = await yandex_gpt.ainvoke(request)
    tokens = await count_tokens_with_ai_message(request, result)
    total_tokens = state["total_tokens"] + tokens
    logger.info(result.content)
    return {"robots_txt": result.content, "total_tokens": total_tokens}


async def get_llms_txt(state: State):
    llms_txt = await get_llms_data(state["url"])
    if llms_txt:
        analyze = await analyze_llms_txt(llms_txt)
        total_tokens = state["total_tokens"] + analyze["total_tokens"]
        return {"total_tokens": total_tokens, "llms_txt": analyze["llms_txt"]}
    generate = await generate_llms_txt(state["markdown"])
    total_tokens = state["total_tokens"] + generate["total_tokens"]
    return {"total_tokens": total_tokens, "llms_txt": generate["llms_txt"]}


builder = StateGraph(State)

builder.add_node("generate_aio_content", generate_aio_content)
builder.add_node("get_lds", get_lds)
builder.add_node("get_robots", get_robots)
builder.add_node("get_llms_txt", get_llms_txt)

builder.add_edge(START, "generate_aio_content")
builder.add_edge("generate_aio_content", "get_lds")
builder.add_edge("get_lds", "get_robots")
builder.add_edge("get_robots", "get_llms_txt")
builder.add_edge("get_llms_txt", END)

agent_aio = builder.compile()
