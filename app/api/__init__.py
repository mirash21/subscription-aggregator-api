from fastapi import APIRouter
from .routes.subscriptions import router as subscriptions_router

router = APIRouter()
router.include_router(subscriptions_router, prefix="/subscriptions", tags=["subscriptions"])

__all__ = ["router"]