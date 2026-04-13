from fastapi import APIRouter

from .auth import router as auth_router
from .invitations import router as invitation_router

router = APIRouter()
router.include_router(auth_router)

router.include_router(invitation_router)
