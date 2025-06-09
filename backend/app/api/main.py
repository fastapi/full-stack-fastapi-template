from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, ceo, manager, supervisor, hr, support, agent, auth, properties, transactions, analytics, credits, financial_analysis
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(ceo.router)
api_router.include_router(manager.router)
api_router.include_router(supervisor.router)
api_router.include_router(hr.router)
api_router.include_router(support.router)
api_router.include_router(agent.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(credits.router, prefix="/credits", tags=["credits"])
api_router.include_router(
    financial_analysis.router,
    prefix="/financial-analysis",
    tags=["financial-analysis"]
)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
