from bs4 import BeautifulSoup

from ...core.depends import (
    parser_markdown,
    yandex_gpt,
)
from ...core.schemas import SEOAnalysisReport
from ...utils.layout_structure import find_seo_issues
from ..prompts import PROMPT_MARKDOWN
from ..utils import count_tokens


async def analyze_markdown(markdown: str) -> dict:
    request = PROMPT_MARKDOWN.format(
        query=markdown, format_instructions=parser_markdown.get_format_instructions()
    )  # noqa: E501, RUF100
    chain = yandex_gpt | parser_markdown
    result: SEOAnalysisReport = await chain.ainvoke(request)
    total_tokens = count_tokens(request, result.model_dump_json())
    return {"result": result.model_dump(), "total_tokens": total_tokens}


async def get_seo_issues(html: str) -> list:
    bs = BeautifulSoup(html, "html.parser")
    return find_seo_issues(bs)
