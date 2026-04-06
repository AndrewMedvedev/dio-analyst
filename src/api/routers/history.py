from fastapi import APIRouter, Depends, status

from ...database.repos.user import UserSEORepository
from ..dependencies import CurrentUserDep, get_repo

router_history = APIRouter()


@router_history.get("/results", status_code=status.HTTP_200_OK)
async def get_results(
    current_user: CurrentUserDep,
    page: int = 1,
    limit: int = 10,
    repository: UserSEORepository = Depends(get_repo),
) -> list:
    return await repository.read_paginated(user_id=current_user.user_id, page=page, limit=limit)
