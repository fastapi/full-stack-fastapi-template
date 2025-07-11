from fastapi import APIRouter

from app.api.routes import (
    items, login, private, users, utils, ceo, manager, supervisor, hr, support, agent, 
    auth, properties, clients, transactions, analytics, credits, financial_analysis, clerk_webhooks, legal, client_dashboard
)
from app.core.config import settings

api_router = APIRouter()

# Webhooks de Clerk (sin autenticación)
api_router.include_router(clerk_webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Rutas de autenticación
api_router.include_router(login.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Rutas de usuarios
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router)
api_router.include_router(items.router)

# Rutas por rol (simplificadas)
api_router.include_router(ceo.router)
api_router.include_router(manager.router)
api_router.include_router(supervisor.router)
api_router.include_router(hr.router)
api_router.include_router(support.router)
api_router.include_router(agent.router)

# Rutas de funcionalidad principales
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(credits.router, prefix="/credits", tags=["credits"])
api_router.include_router(financial_analysis.router, prefix="/financial", tags=["financial"])
api_router.include_router(legal.router, prefix="/legal", tags=["legal"])
api_router.include_router(client_dashboard.router, prefix="/client", tags=["client"])

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
