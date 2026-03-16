import asyncio
import logging

from playwright.async_api import async_playwright

from ..agents.subagents.process import generate_json_ld
from ..utils.web_parser import get_markdown_content


async def parce(url: str) -> str:
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
            return await get_markdown_content(browser, url)
        finally:
            await browser.close()


async def main(url: str):
    parce_ = await parce(url)
    result = await generate_json_ld(parce_)
    print(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main("https://arsplus.ru"))
