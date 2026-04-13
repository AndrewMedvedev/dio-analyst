__all__ = [
    "INDEX_NAME",
    "AppError",
    "Base",
    "InvitationOrm",
    "SEOResultOrm",
    "UserOrm",
    "client",
    "delete_old_data",
    "router",
]

from fastapi import APIRouter

from .errors import AppError
from .iam.api import router as router_iam
from .iam.database.base import Base
from .iam.database.models import (
    InvitationOrm,
    UserOrm,
)
from .seo.agents.rag import INDEX_NAME, client, delete_old_data
from .seo.api import router as router_seo
from .seo.database.repository import SEOResultOrm

router = APIRouter(prefix="/api/v1")
router.include_router(router_seo)
router.include_router(router_iam)
