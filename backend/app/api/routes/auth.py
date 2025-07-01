from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    """Estado de autenticación"""
    return {"status": "Auth system using Clerk"} 