from fastapi import APIRouter

from .chat import router_chat
from .history import router_history
from .seo import router_seo

router = APIRouter()
router.include_router(router_seo)
router.include_router(router_chat)
router.include_router(router_history)
