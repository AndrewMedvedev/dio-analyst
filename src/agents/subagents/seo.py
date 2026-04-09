import json
import logging
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from ...core.depends import (
    cwv_prompt_template,
    gpt_oss_120b,
    parser_cwv,
    parser_result,
    text_splitter,
    yandex_gpt,
)
from ...integrations.google_psi_api import run_page_speed
from ...schemas import CWVReport, SiteAnalysisReport
from ..prompts import PROMPT_RESULT
from .process import analyze_markdown
from .utils import get_seo_issues

logger = logging.getLogger(__name__)


class State(TypedDict):
    url: str
    markdown: list[str]
    html: str
    analyze_md: dict
    seo_issue: list[dict]
    cwv: CWVReport
    result: SiteAnalysisReport
    total_tokens: Annotated[int, operator.add]
    total_money: Annotated[float, operator.add]


async def analyze_markups(state: State) -> dict:
    result, tokens = await analyze_markdown(state["markdown"])
    total_tokens = tokens + state.get("total_tokens", 0)
    seo_issue = await get_seo_issues(state["html"])
    logger.info("Анализ разметки сайта")
    return {
        "analyze_md": result,
        "seo_issue": seo_issue,
        "total_tokens": total_tokens,
    }


async def get_core_web_vitals(state: State) -> dict:
    cwv = await run_page_speed(state["url"])
    chain = cwv_prompt_template | yandex_gpt | parser_cwv
    count_cwv = yandex_gpt.get_num_tokens(str(cwv))
    result: CWVReport = await chain.ainvoke({"query": cwv})
    count_result = yandex_gpt.get_num_tokens(str(result))
    total_tokens = count_cwv + count_result + state.get("total_tokens", 0)
    logger.info("Получение CWV")
    total_money = (total_tokens / 1000 * 0.80) + state.get("total_money", 0)
    return {"cwv": result.model_dump(), "total_tokens": total_tokens, "total_money": total_money}


async def final_result(state: State) -> dict:
    chain = gpt_oss_120b | parser_result
    dumps_issue = json.dumps(state["seo_issue"])
    split_issue = text_splitter.split_text(dumps_issue)
    request = PROMPT_RESULT.format(
        markdown=state["markdown"],
        seo_issue=split_issue,
        cwv=state["cwv"],
        format_instructions=parser_result.get_format_instructions(),
    )
    count_data = yandex_gpt.get_num_tokens(request)

    result: SiteAnalysisReport = await chain.ainvoke(request)
    count_result = yandex_gpt.get_num_tokens(result.model_dump_json())
    tokens = count_data + count_result
    total_tokens = state["total_tokens"] + tokens
    logger.info("Результат SEO")
    total_money = (tokens / 1000 * 0.30) + state["total_money"]
    return {"result": result.to_dict, "total_tokens": total_tokens, "total_money": total_money}


builder = StateGraph(State)

builder.add_node("analyze_markups", analyze_markups)
builder.add_node("get_core_web_vitals", get_core_web_vitals)
builder.add_node("final_result", final_result)

builder.add_edge(START, "analyze_markups")
builder.add_edge(START, "get_core_web_vitals")

builder.add_edge("analyze_markups", "final_result")
builder.add_edge("get_core_web_vitals", "final_result")

builder.add_edge("final_result", END)

agent_seo = builder.compile()
