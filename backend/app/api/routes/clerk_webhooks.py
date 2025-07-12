import hmac
import hashlib
import json
import logging
from fastapi import APIRouter, Request, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import uuid
import httpx

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
            # Obtener el correo del usuario
            email = user_data.get("email_addresses", [{}])[0].get("email_address", "")
            
            # Determinar el rol del usuario
            role = "agent"  # Rol por defecto
            
            # Verificar si es el correo del CEO
            if email.lower() == settings.CEO_USER.lower():
                role = "ceo"
                print(f"Usuario CEO detectado: {email}")
                
                # Actualizar el public_metadata en Clerk para el usuario CEO
                await update_clerk_user_metadata(user_data.get("id"), {"role": "ceo"})
            
            # Crear usuario en PostgreSQL
            user = User(
                id=uuid.uuid4(),
                clerk_id=user_data.get("id"),
                email=email,
                full_name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                is_active=True,
                role=role,
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

async def update_clerk_user_metadata(user_id: str, metadata: dict):
    """Actualizar los metadatos de un usuario en Clerk"""
    try:
        headers = {
            "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        # Actualizar los metadatos públicos del usuario
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.clerk.com/v1/users/{user_id}/metadata",
                headers=headers,
                json={"public_metadata": metadata}
            )
            
            if response.status_code != 200:
                logger.error(f"Error actualizando metadatos en Clerk: {response.text}")
                return False
                
            logger.info(f"Metadatos actualizados en Clerk para el usuario {user_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error en update_clerk_user_metadata: {e}")
        return False

async def handle_user_updated(user_data: dict):
    """Manejar actualización de usuario en Clerk"""
    try:
        with Session(engine) as session:
            # Buscar usuario por clerk_id
            statement = select(User).where(User.clerk_id == user_data.get("id"))
            user = session.exec(statement).first()
            
            if user:
                # Obtener el correo del usuario
                email = user_data.get("email_addresses", [{}])[0].get("email_address", user.email)
                
                # Verificar si es el correo del CEO
                if email.lower() == settings.CEO_USER.lower():
                    # Actualizar el rol a CEO tanto en la base de datos como en Clerk
                    user.role = "ceo"
                    await update_clerk_user_metadata(user_data.get("id"), {"role": "ceo"})
                
                # Actualizar otros datos del usuario
                user.email = email
                user.full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                user.phone = user_data.get("phone_numbers", [{}])[0].get("phone_number", user.phone)
                user.updated_at = datetime.utcnow()
                
                session.add(user)
                session.commit()
                
                logger.info(f"Usuario actualizado: {user.email} (Rol: {user.role})")
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