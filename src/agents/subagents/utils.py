import logging

from bs4 import BeautifulSoup
from langchain.messages import AIMessage

from ...core.depends import (
    parser_markdown,
    yandex_gpt,
)
from ...core.schemas import SEOAnalysisReport
from ...utils.layout_structure import find_seo_issues
from ..prompts import (
    PROMPT_ANALYZE_JSON_LD,
    PROMPT_ANALYZE_LLMS_TXT,
    PROMPT_GENERATE_JSON_LD,
    PROMPT_GENERATE_LLMS_TXT,
    PROMPT_MARKDOWN,
    PROMPT_SUMMARIZE,
)

logger = logging.getLogger(__name__)


async def count_tokens_with_ai_message(request: str, result: AIMessage) -> int:
    count_request = yandex_gpt.get_num_tokens(request)
    count_result = yandex_gpt.get_num_tokens(str(result.content))
    return count_request + count_result


async def count_tokens(request: str, result: str) -> int:
    count_request = yandex_gpt.get_num_tokens(request)
    count_result = yandex_gpt.get_num_tokens(result)
    return count_request + count_result


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


async def analyze_markdown(markdown: str) -> dict:
    request = PROMPT_MARKDOWN.format(
        query=markdown, format_instructions=parser_markdown.get_format_instructions()
    )  # noqa: E501, RUF100
    chain = yandex_gpt | parser_markdown
    result: SEOAnalysisReport = await chain.ainvoke(request)
    total_tokens = await count_tokens(request, result.model_dump_json())
    return {"result": result.model_dump(), "total_tokens": total_tokens}


async def get_seo_issues(html: str) -> list:
    bs = BeautifulSoup(html, "html.parser")
    issue = find_seo_issues(bs)
    return [i.model_dump() for i in issue]


ab_queries = [
    "1с комплексная автоматизация цена",
    "сопровождение 1с архитектор бизнеса",
    "1с:зарплата и управление персоналом",
    "обучение 1с архитектор бизнеса",
    "1с",
    "архитектор бизнеса",
    "1с управление небольшой фирмой",
    "1с бухгалтерия архитектор",
    "внедрение 1с архитектор",
    "1с строительство архитектор",
    "обновление 1с архитектор бизнеса",
    "1с архитектор бизнеса",
    "1с камин архитектор",
    "1с документооборот архитектор",
    "купить 1с у архитектора",
    "отзывы архитектор бизнеса",
    "переход на 1с с архитектором",
    "1с отчетность архитектор",
]

one_bit_queries = [
    "1с документооборот первый бит",
    "внедрение 1с первый бит",
    "обновление 1с первый бит",
    "отзывы о первом бите",
    "1с первый бит",
    "цена 1с бухгалтерия базовая",
    "1с бухгалтерия цена",
    "переход на 1с с первого бита",
    "первый бит",
    "1с отчетность первый бит",
    "аренда 1с в облаке первый бит",
    "купить 1с в первом бите",
    "1с управление торговлей",
    "1с комплексная автоматизация первый бит",
    "курсы 1с первый бит",
    "1с",
    "1с:предприятие",
    "обслуживание 1с первый бит",
]
