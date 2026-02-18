import asyncio
import json
import pathlib

from src.agents.agent_analyst.agent import agent_analyst, get_markdown


async def main():
    # result = await get_markdown("https://www.1ab.ru")
    result = await agent_analyst.ainvoke({"url": "https://www.1ab.ru"})
    print(result)
    pathlib.Path("analyst.json").write_text(  # noqa: ASYNC240
        json.dumps(str(result), ensure_ascii=False, indent=2), encoding="utf-8"
    )


asyncio.run(main())
# from src.api.router import create_fastapi_app

# app = create_fastapi_app()

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
