#!/usr/bin/env python3
"""
Script simple para actualizar el rol del usuario CEO
"""
import sys
import os
import asyncio

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_path)

async def update_ceo_role():
    """Actualizar el rol del usuario CEO en la base de datos"""
    try:
        # Importaciones locales
        from app.core.db import get_session_context
        from app.models import User, UserRole
        from sqlmodel import select
        
        print("👑 GENIUS INDUSTRIES - Actualización de Rol CEO")
        print("=" * 60)
        
        # ID del usuario CEO de Clerk
        ceo_clerk_id = "user_2zJmXcYVnqG5nvgjTsrAWv1fO88"
        ceo_email = "ceo@geniusindustries.org"
        
        async with get_session_context() as session:
            # Buscar usuario por Clerk ID
            stmt = select(User).where(User.clerk_id == ceo_clerk_id)
            result = await session.exec(stmt)
            user = result.first()
            
            if not user:
                # Buscar por email
                stmt = select(User).where(User.email == ceo_email)
                result = await session.exec(stmt)
                user = result.first()
                
                if user:
                    print(f"✅ Usuario encontrado por email: {user.email}")
                    # Actualizar Clerk ID
                    user.clerk_id = ceo_clerk_id
                    session.add(user)
                    print(f"✅ Clerk ID actualizado: {ceo_clerk_id}")
                else:
                    print(f"❌ Usuario no encontrado ni por Clerk ID ni por email")
                    return
            else:
                print(f"✅ Usuario encontrado por Clerk ID: {user.email}")
            
            # Actualizar rol a CEO
            if user.role != UserRole.CEO:
                user.role = UserRole.CEO
                user.is_superuser = True
                session.add(user)
                print(f"✅ Rol actualizado a: {UserRole.CEO}")
                print(f"✅ Superuser activado: True")
            else:
                print(f"ℹ️  Usuario ya tiene rol CEO")
            
            # Confirmar cambios
            await session.commit()
            print(f"✅ Cambios guardados exitosamente")
            
            # Verificar datos finales
            print("\n📊 Estado final del usuario:")
            print(f"   Email: {user.email}")
            print(f"   Clerk ID: {user.clerk_id}")
            print(f"   Rol: {user.role}")
            print(f"   Superuser: {user.is_superuser}")
            print(f"   Activo: {user.is_active}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_ceo_role()) 