from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from playwright.async_api import async_playwright
from pydantic import HttpUrl

from ..utils.tree import PRIORITY_KEYWORDS, TreeNode, build_site_tree, extract_key_pages
from ..utils.web_parser import get_html_content, get_markdown_content


class State(TypedDict):
    url: str
    max_result: int
    site_map: TreeNode
    pages: list[HttpUrl]
    markdown: list[dict]
    html: list[dict]


async def get_site_markups(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        try:
            markdown = await get_markdown_content(browser, url)
            html = await get_html_content(browser, url)
            return {"markdown": markdown, "html": html}
        finally:
            await browser.close()


async def get_site_map(state: State) -> dict:
    result = build_site_tree(HttpUrl(state["url"]))
    return {"site_map": result}


async def get_site_pages(state: State) -> dict:
    site_tree = state["site_map"]
    result = extract_key_pages(
        site_tree,
        key_segments=PRIORITY_KEYWORDS,  # type: ignore  # noqa: PGH003
        max_result=state["max_result"],
    )
    return {"pages": result}


async def get_markups(state: State) -> dict:
    html: list = []
    markdown: list = []
    for i in state["pages"]:
        markups = await get_site_markups(str(i))
        html.append({"url": i, "html": markups["html"]})
        markdown.append({"url": i, "markdown": markups["markdown"]})
    return {"html": html, "markdown": markdown}


builder = StateGraph(State)
builder.add_node("get_site_map", get_site_map)
builder.add_node("get_site_pages", get_site_pages)
builder.add_node("get_markups", get_markups)

builder.add_edge(START, "get_site_map")
builder.add_edge("get_site_map", "get_site_pages")
builder.add_edge("get_site_pages", "get_markups")
builder.add_edge("get_markups", END)

agent_importer = builder.compile()
