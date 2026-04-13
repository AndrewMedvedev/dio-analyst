import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, status
from pydantic import HttpUrl

from ....seo.agents import rag
from ....seo.agents.subagents import agent_aio
from ....seo.agents.subagents.utils import parce_site_markups
from ....seo.agents.workflow import agent
from ...database.repository import UserSEORepository
from ...schemas import SEOResult
from ..dependencies import CurrentUserDep, get_repo

router_seo = APIRouter()


@router_seo.get("/seo", status_code=status.HTTP_200_OK)
async def get_seo(
    url: HttpUrl,
    current_user: CurrentUserDep,
    repository: UserSEORepository = Depends(get_repo),
) -> dict:
    url_str = url.encoded_string()
    result = await agent.ainvoke({"url": url_str})  # type: ignore  # noqa: PGH003
    del result["html"]
    del result["markdown"]

    generation_id = str(uuid4())
    await rag.indexing(
        text=json.dumps(result),
        metadata={
            "tenant_id": str(current_user.user_id),
            "timestamp": int(datetime.now(UTC).timestamp()),
            "generation_id": generation_id,
        },
    )

    result["generation_id"] = generation_id
    schema = SEOResult(user_id=current_user.user_id, result=result)  # type: ignore  # noqa: PGH003
    await repository.create(entity=schema)
    return result


@router_seo.get("/aio/{generation_id}", status_code=status.HTTP_200_OK)
async def get_aio(
    url: HttpUrl,
    current_user: CurrentUserDep,
    generation_id: str,
    repository: UserSEORepository = Depends(get_repo),
) -> dict:
    url_str = url.encoded_string()
    markdown, html = await parce_site_markups(url_str)  # type: ignore  # noqa: PGH003
    result = await agent_aio.ainvoke(
        {"url": url_str, "html": html, "markdown": markdown}  # type: ignore  # noqa: PGH003
    )  # type: ignore  # noqa: PGH003
    del result["html"]
    del result["markdown"]
    await rag.indexing(
        text=json.dumps(result),
        metadata={
            "tenant_id": str(current_user.user_id),
            "timestamp": int(datetime.now(UTC).timestamp()),
            "generation_id": generation_id,
        },
    )

    result["generation_id"] = generation_id
    schema = SEOResult(user_id=current_user.user_id, result=result)  # type: ignore  # noqa: PGH003
    await repository.create(entity=schema)
    return result
