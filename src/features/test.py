import asyncio
import base64
import mimetypes
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage
from playwright.async_api import async_playwright

from ..agents.prompts import PROMPT_GENERATE_ALT
from ..core.depends import gemma_3_27b_it
from ..utils.web_parser import get_html_content


async def get_images(url: str) -> list:
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
            html = await get_html_content(browser, url)
            soup = BeautifulSoup(html, "html.parser")
            all_images = soup.find_all("img")
            links: list = []
            for data in all_images:
                alt, src = data.get("alt", ""), data.get("src", "")
                if alt == "":
                    links.append({"url": urljoin("https://arsplus.ru", src), "alt": alt})  # type: ignore  # noqa: PGH003
                continue
            return links

        finally:
            await browser.close()


async def get_mime(url: str, byte: bytes) -> str:
    mime_type, _ = mimetypes.guess_type(url)
    if not mime_type:
        # Простейшая проверка по сигнатуре файла
        if byte.startswith(b"\xff\xd8"):
            mime_type = "image/jpeg"
        elif byte.startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        elif byte.startswith((b"GIF87a", b"GIF89a")):
            mime_type = "image/gif"
        elif byte.startswith(b"RIFF") and byte[8:12] == b"WEBP":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"  # fallback
    return mime_type


async def parce_images(links: list[str]) -> tuple:
    result = []
    total_tokens = 0
    images = []
    for image in links:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url=image["url"], ssl=False) as response,  # type: ignore  # noqa: PGH003
        ):
            byte = await response.read()
            mime = await get_mime(url=image["url"], byte=byte)  # type: ignore  # noqa: PGH003
            base64_str = base64.b64encode(byte).decode("utf-8")
            images.append({"image": base64_str, "type": mime, "url": image["url"]})  # type: ignore  # noqa: PGH003
            if len(images) != 2:
                continue
            answer, tokens = await generate_alt(images)
            images.clear()
            result.append(answer)
            total_tokens += tokens
    if images:
        answer, tokens = await generate_alt(images)
        images.clear()
        result.append(answer)
        total_tokens += tokens

    return result, total_tokens


async def generate_alt(data: list) -> tuple:
    request = PROMPT_GENERATE_ALT.format(urls=[i["url"] for i in data])
    message = [
        {
            "type": "text",
            "text": request,
        }
    ]
    for i in data:
        message.append(  # noqa: PERF401
            {"type": "image_url", "image_url": {"url": f"data:{i['type']};base64,{i['image']}"}}  # type: ignore  # noqa: PGH003
        )
    await asyncio.sleep(2)
    answer = await gemma_3_27b_it.ainvoke([HumanMessage(content=message)])
    print(answer.content)
    print(answer.usage_metadata["total_tokens"])
    return answer.content, answer.usage_metadata["total_tokens"]


links = asyncio.run(get_images("https://arsplus.ru"))
images, tokens = asyncio.run(parce_images(links))
print(images)
print()
print(tokens)

"Вот предложенные alt-тексты для изображений:"
"alt: Логотип АРСЕНАЛ+: надежный поставщик решений"
"url: https://arsplus.ru/upload/arsenalcv_2.png"
"alt: Кнопка Получить консультацию - красного цвета"
"url: https://arsplus.ru/new/img/Link%20%2814%29.webp"
"alt: Красная кнопка Подобрать решение со стрелкой"
"url: https://arsplus.ru/local/templates/main/images/link.png"
