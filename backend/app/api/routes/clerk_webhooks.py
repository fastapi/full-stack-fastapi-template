import hmac
import hashlib
import json
import logging
from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.db import engine
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verificar la firma del webhook de Clerk"""
    if not signature.startswith("v1,"):
        return False
    
    timestamp = signature.split(",")[0][3:]  # Remover 'v1,' del inicio
    sig = signature.split(",")[1]
    
    # Crear el payload para verificar
    webhook_payload = f"{timestamp}.{payload.decode()}"
    
    # Calcular la firma esperada
    expected_sig = hmac.new(
        secret.encode(),
        webhook_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(sig, expected_sig)

@router.post("/clerk/webhook")
async def clerk_webhook(request: Request):
    """Manejar webhooks de Clerk para sincronizar usuarios"""
    try:
        # Obtener el payload y la firma
        payload = await request.body()
        signature = request.headers.get("svix-signature", "")
        
        # Verificar la firma si hay un secret configurado
        if settings.CLERK_WEBHOOK_SECRET:
            if not verify_webhook_signature(payload, signature, settings.CLERK_WEBHOOK_SECRET):
                logger.warning("Firma de webhook inválida")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Firma inválida"
                )
        
        # Parsear el payload
        data = json.loads(payload.decode())
        event_type = data.get("type")
        user_data = data.get("data", {})
        
        logger.info(f"Webhook recibido: {event_type}")
        
        # Procesar diferentes tipos de eventos
        if event_type == "user.created":
            await handle_user_created(user_data)
        elif event_type == "user.updated":
            await handle_user_updated(user_data)
        elif event_type == "user.deleted":
            await handle_user_deleted(user_data)
        else:
            logger.info(f"Evento no manejado: {event_type}")
        
        return {"status": "success"}
        
    except json.JSONDecodeError:
        logger.error("Error decodificando JSON del webhook")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON inválido"
        )
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

async def handle_user_created(user_data: dict):
    """Manejar creación de usuario en Clerk"""
    try:
        with Session(engine) as session:
            # Crear usuario en PostgreSQL
            user = User(
                id=uuid.uuid4(),
                clerk_id=user_data.get("id"),
                email=user_data.get("email_addresses", [{}])[0].get("email_address", ""),
                full_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                is_active=True,
                role=user_data.get("public_metadata", {}).get("role", "agent"),
                phone=user_data.get("phone_numbers", [{}])[0].get("phone_number", None),
                created_at=datetime.utcnow(),
                hashed_password=""
            )
            
            session.add(user)
            session.commit()
            
            logger.info(f"Usuario creado: {user.email}")
            
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        raise

async def handle_user_updated(user_data: dict):
    """Manejar actualización de usuario en Clerk"""
    try:
        with Session(engine) as session:
            # Buscar usuario por clerk_id
            statement = select(User).where(User.clerk_id == user_data.get("id"))
            user = session.exec(statement).first()
            
            if user:
                # Actualizar datos
                user.email = user_data.get("email_addresses", [{}])[0].get("email_address", user.email)
                user.full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                user.role = user_data.get("public_metadata", {}).get("role", user.role)
                user.phone = user_data.get("phone_numbers", [{}])[0].get("phone_number", user.phone)
                user.updated_at = datetime.utcnow()
                
                session.add(user)
                session.commit()
                
                logger.info(f"Usuario actualizado: {user.email}")
            else:
                logger.warning(f"Usuario no encontrado para actualizar: {user_data.get('id')}")
                
    except Exception as e:
        logger.error(f"Error actualizando usuario: {e}")
        raise

async def handle_user_deleted(user_data: dict):
    """Manejar eliminación de usuario en Clerk"""
    try:
        with Session(engine) as session:
            # Buscar usuario por clerk_id
            statement = select(User).where(User.clerk_id == user_data.get("id"))
            user = session.exec(statement).first()
            
            if user:
                # Marcar como inactivo en lugar de eliminar
                user.is_active = False
                user.updated_at = datetime.utcnow()
                
                session.add(user)
                session.commit()
                
                logger.info(f"Usuario desactivado: {user.email}")
            else:
                logger.warning(f"Usuario no encontrado para eliminar: {user_data.get('id')}")
                
    except Exception as e:
        logger.error(f"Error eliminando usuario: {e}")
        raise 