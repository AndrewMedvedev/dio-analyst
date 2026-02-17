from urllib.parse import urlparse

from aiohttp import ClientSession
from extruct.jsonld import JsonLdExtractor


def parse_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def get_json_ld(html: str) -> list:
    jslde = JsonLdExtractor()
    return jslde.extract(html)


async def get_llms_data(url: str) -> str:
    async with ClientSession() as session, session.get(f"{url}/llms.txt") as data:
        try:
            result = await data.text()
            return result if "html" not in result else ""
        except:
            return ""


async def get_robots_data(url: str) -> str:
    async with ClientSession() as session, session.get(f"{url}/robots.txt") as data:
        try:
            result = await data.text()
            return result if "html" not in result else ""
        except:
            return ""
