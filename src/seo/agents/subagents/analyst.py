import logging
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from ...core.depends import (
    gpt_oss_120b,
    parser_expertise,
    parser_specialization,
)
from ...schemas import ExpertiseSite, SpecializationSite
from ..prompts import PROMPT_EXPERTISE, PROMPT_SPECIALIZATION
from .utils import count_tokens

logger = logging.getLogger(__name__)


class State(TypedDict):
    url: str
    markdown: list[str]
    specialization: dict
    expertise: dict
    semantic_core: dict
    total_tokens: Annotated[int, operator.add]
    total_money: Annotated[float, operator.add]


async def get_specialization(state: State) -> dict:
    request = PROMPT_SPECIALIZATION.format(
        format_instructions=parser_specialization.get_format_instructions(), data=state["markdown"]
    )
    chain = gpt_oss_120b | parser_specialization
    result: SpecializationSite = await chain.ainvoke(request)
    total_tokens = await count_tokens(request, result.model_dump_json()) + state.get(
        "total_tokens", 0
    )
    logger.info("Получения специализации компании")
    total_money = (total_tokens / 1000 * 0.30) + state.get("total_money", 0)
    return {
        "specialization": result.model_dump(),
        "total_tokens": total_tokens,
        "total_money": total_money,
    }


async def get_expertise(state: State) -> dict:
    chain = gpt_oss_120b | parser_expertise
    request = PROMPT_EXPERTISE.format(
        data=state["markdown"],
        format_instructions=parser_expertise.get_format_instructions(),
    )
    result: ExpertiseSite = await chain.ainvoke(request)
    tokens = await count_tokens(request, result.model_dump_json())
    total_tokens = tokens + state.get("total_tokens", 0)
    logger.info("Получения экспертизы компании")
    total_money = (tokens / 1000 * 0.30) + state.get("total_money", 0)
    return {
        "total_tokens": total_tokens,
        "expertise": result.model_dump(),
        "total_money": total_money,
    }


"""async def get_semantic_core(state: State) -> dict:
    request = PROMPT_SEMANTIC_CORE.format(
        data=..., format_instructions=parser_sc.get_format_instructions()
    )
    chain = yandex_gpt | parser_sc
    result: SemanticCore = await chain.ainvoke(request)
    tokens = await count_tokens(request, result.model_dump_json())
    total_tokens = tokens + state["total_tokens"]
    logger.info("Получения семантического ядра компании")
    total_money = (tokens / 1000 * 0.80) + state["total_money"]
    return {
        "total_tokens": total_tokens,
        "semantic_core": result.model_dump(),
        "total_money": total_money,
    }
"""

builder = StateGraph(State)

builder.add_node("get_specialization", get_specialization)
builder.add_node("get_expertise", get_expertise)
"""builder.add_node("get_semantic_core", get_semantic_core)"""

builder.add_edge(START, "get_specialization")
builder.add_edge(START, "get_expertise")
builder.add_edge("get_specialization", END)
builder.add_edge("get_expertise", END)

agent_analyst = builder.compile()
