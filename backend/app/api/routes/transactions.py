from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/")
async def get_transactions(current_user: CurrentUser, session: SessionDep):
    """Obtener todas las transacciones"""
    return {
        "message": "Transactions endpoint",
        "user": current_user,
        "transactions": []
    }


@router.post("/")
async def create_transaction(current_user: CurrentUser, session: SessionDep):
    """Crear una nueva transacción"""
    return {
        "message": "Create transaction - Coming soon",
        "user": current_user
    }
