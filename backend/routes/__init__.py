"""
API Routes
"""
from fastapi import APIRouter
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.users import router as users_router
from routes.integrations import router as integrations_router
from routes.trading import router as trading_router
from routes.user_management import router as user_management_router
from routes.sec import router as sec_router
from routes.ingestion import router as ingestion_router
from routes.billing import router as billing_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["integrations"])
api_router.include_router(trading_router, prefix="/trading", tags=["trading"])
api_router.include_router(user_management_router, prefix="/user-management", tags=["user-management"])
api_router.include_router(sec_router, prefix="/sec", tags=["sec"])
api_router.include_router(ingestion_router)  # Already has prefix in file
api_router.include_router(billing_router)  # Already has prefix in file
