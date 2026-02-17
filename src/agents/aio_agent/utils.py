import logging

from ...core.depends import yandex_gpt
from ..prompts import (
    PROMPT_ANALYZE_JSON_LD,
    PROMPT_ANALYZE_LLMS_TXT,
    PROMPT_GENERATE_JSON_LD,
    PROMPT_GENERATE_LLMS_TXT,
    PROMPT_SUMMARIZE,
)
from ..utils import count_tokens_with_ai_message

logger = logging.getLogger(__name__)


async def analyze_json_ld(ld: list) -> dict:
    request = PROMPT_ANALYZE_JSON_LD.format(json_ld=ld)
    result = await yandex_gpt.ainvoke(request)
    total_tokens = await count_tokens_with_ai_message(request, result)
    logger.info(result.content)
    return {"json_ld": result.content, "total_tokens": total_tokens}


async def generate_json_ld(markdown: str) -> dict:
    request = PROMPT_GENERATE_JSON_LD.format(data=markdown)
    result = await yandex_gpt.ainvoke(request)
    total_tokens = await count_tokens_with_ai_message(request, result)
    logger.info(result.content)
    return {"json_ld": result.content, "total_tokens": total_tokens}


async def analyze_llms_txt(txt: str) -> dict:
    request = PROMPT_ANALYZE_LLMS_TXT.format(data=txt)
    result = await yandex_gpt.ainvoke(request)
    total_tokens = await count_tokens_with_ai_message(request, result)
    logger.info(result.content)
    return {"llms_txt": result.content, "total_tokens": total_tokens}


async def generate_llms_txt(markdowns: list[dict]) -> dict:
    data_all = []
    total_tokens = 0
    for i in markdowns:
        request_summarize = PROMPT_SUMMARIZE.format(data=i["markdown"])
        summarize = await yandex_gpt.ainvoke(request_summarize)
        tokens = await count_tokens_with_ai_message(request_summarize, summarize)
        total_tokens += tokens
        data = {"url": i["url"], "data": summarize.content}
        data_all.append(data)
    request = PROMPT_GENERATE_LLMS_TXT.format(data=data_all)
    result = await yandex_gpt.ainvoke(request)
    count = await count_tokens_with_ai_message(request, result)
    total_tokens += count
    logger.info(result.content)
    return {"llms_txt": result.content, "total_tokens": total_tokens}
