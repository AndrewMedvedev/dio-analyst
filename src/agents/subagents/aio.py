import logging
import operator
from typing import Annotated, TypedDict

from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from ...core.depends import gpt_oss_120b, parser_aio_content, yandex_gpt
from ...schemas import GenerateAIOContent
from ...utils.checkup import get_json_ld, get_llms_data, get_robots_data
from ..prompts import PROMPT_ANALYZE_ROBOTS, PROMPT_GENERATE_AIO_CONTENT
from .process import (
    analyze_json_ld,
    analyze_llms_txt,
    generate_json_ld,
    generate_llms_txt,
)
from .utils import count_tokens

logger = logging.getLogger(__name__)


class State(TypedDict):
    url: str
    markdown: list[str]
    html: str
    new_content: dict
    json_ld: dict
    robots_txt: str
    llms_txt: str
    total_tokens: Annotated[int, operator.add]
    total_money: Annotated[float, operator.add]


async def generate_aio_content(state: State) -> dict:
    chain = gpt_oss_120b | parser_aio_content
    request = PROMPT_GENERATE_AIO_CONTENT.format(
        data=state["markdown"], format_instructions=parser_aio_content.get_format_instructions()
    )
    result: GenerateAIOContent = await chain.ainvoke(request)
    logger.info("Генерация AIO контента")
    total_tokens = await count_tokens(request, result.model_dump_json()) + state.get(
        "total_tokens", 0
    )
    total_money = (total_tokens / 1000 * 0.30) + state.get("total_money", 0)
    return {
        "total_tokens": total_tokens,
        "total_money": total_money,
        "new_content": result.model_dump(),
    }


async def create_lds(state: State) -> dict:
    ld = get_json_ld(state["html"])
    if ld != []:
        analyze = await analyze_json_ld(ld)
        logger.info("Анализ json-ld контента")
        total_money = (analyze["total_tokens"] / 1000 * 0.80) + state.get("total_money", 0)
        return {
            "json_ld": analyze["json_ld"],
            "total_tokens": analyze["total_tokens"] + state.get("total_tokens", 0),
            "total_money": total_money,
        }
    generate = await generate_json_ld(state["markdown"])
    logger.info("Генерация json-ld контента")
    total_money = (generate["total_tokens"] / 1000 * 0.30) + state.get("total_money", 0)
    return {
        "json_ld": generate["json_ld"],
        "total_tokens": generate["total_tokens"] + state.get("total_tokens", 0),
        "total_money": total_money,
    }


async def change_robots_txt(state: State) -> dict:
    data = await get_robots_data(state["url"])
    request = PROMPT_ANALYZE_ROBOTS.format(data=data)
    result: AIMessage = await yandex_gpt.ainvoke(request)
    tokens = result.usage_metadata["total_tokens"]  # type: ignore  # noqa: PGH003
    total_tokens = state.get("total_tokens", 0) + tokens
    total_money = (tokens / 1000 * 0.80) + state.get("total_money", 0)
    logger.info("Изменение robots.txt")
    return {"robots_txt": result.content, "total_tokens": total_tokens, "total_money": total_money}


async def create_llms_txt(state: State):
    llms_txt = await get_llms_data(state["url"])
    if llms_txt:
        analyze = await analyze_llms_txt(llms_txt)
        total_tokens = state.get("total_tokens", 0) + analyze["total_tokens"]
        total_money = (analyze["total_tokens"] / 1000 * 0.30) + state.get("total_money", 0)
        logger.info("Анализ llms контента")
        return {
            "total_tokens": total_tokens,
            "llms_txt": analyze["llms_txt"],
            "total_money": total_money,
        }
    generate = await generate_llms_txt(state["markdown"], url=state["url"])
    total_tokens = state.get("total_tokens", 0) + generate["total_tokens"]
    logger.info("Генерация llms контента")
    total_money = (generate["total_tokens"] / 1000 * 0.30) + state.get("total_money", 0)
    return {
        "total_tokens": total_tokens,
        "total_money": total_money,
        "llms_txt": generate["llms_txt"],
    }


builder = StateGraph(State)

builder.add_node("generate_aio_content", generate_aio_content)
builder.add_node("create_lds", create_lds)
builder.add_node("change_robots_txt", change_robots_txt)
builder.add_node("create_llms_txt", create_llms_txt)

builder.add_edge(START, "generate_aio_content")
builder.add_edge(START, "create_lds")
builder.add_edge(START, "change_robots_txt")
builder.add_edge(START, "create_llms_txt")

builder.add_edge("generate_aio_content", END)
builder.add_edge("create_lds", END)
builder.add_edge("change_robots_txt", END)
builder.add_edge("create_llms_txt", END)

agent_aio = builder.compile()
