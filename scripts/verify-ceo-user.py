#!/usr/bin/env python3
"""
🔍 Verificación de Usuario CEO - GENIUS INDUSTRIES
Script para verificar que el usuario CEO tenga acceso completo al sistema
"""

import os
import sys
import asyncio
from pathlib import Path

# Agregar el directorio del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

async def verify_ceo_user():
    """Verificar configuración del usuario CEO"""
    
    try:
        # Importar dependencias del backend
        from app.core.db import get_session
        from app.models import User
        from sqlalchemy import select, text
        from passlib.context import CryptContext
        
        print("🔍 Verificando configuración de usuario CEO...")
        
        # Configuración de variables
        ceo_email = os.getenv("CEO_USER", "ceo@geniusindustries.org")
        ceo_password = os.getenv("CEO_USER_PASSWORD", "GeniusCEO2025!")
        
        print(f"📧 Email CEO: {ceo_email}")
        
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        
        async with get_session() as session:
            
            # 1. Verificar conexión a la base de datos
            try:
                result = await session.execute(text("SELECT 1"))
                print("✅ Conexión a base de datos: OK")
            except Exception as e:
                print(f"❌ Error de conexión a base de datos: {e}")
                return False
            
            # 2. Verificar si existe la tabla users
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user'"))
                count = result.scalar()
                if count > 0:
                    print("✅ Tabla 'user' existe")
                else:
                    print("❌ Tabla 'user' no existe")
                    return False
            except Exception as e:
                print(f"❌ Error verificando tabla users: {e}")
                return False
            
            # 3. Verificar si existe el usuario CEO
            try:
                stmt = select(User).where(User.email == ceo_email)
                result = await session.execute(stmt)
                ceo_user = result.scalar_one_or_none()
                
                if ceo_user:
                    print("✅ Usuario CEO encontrado")
                    print(f"   - ID: {ceo_user.id}")
                    print(f"   - Nombre: {ceo_user.full_name}")
                    print(f"   - Role: {ceo_user.role}")
                    print(f"   - Activo: {ceo_user.is_active}")
                    print(f"   - Superuser: {ceo_user.is_superuser}")
                    print(f"   - Teléfono: {ceo_user.phone}")
                    
                    # Verificar permisos
                    if ceo_user.role == "CEO" and ceo_user.is_superuser and ceo_user.is_active:
                        print("✅ Permisos CEO: Acceso completo configurado")
                    else:
                        print("⚠️  Permisos CEO: Configuración incompleta")
                        
                    # Verificar contraseña
                    if pwd_context.verify(ceo_password, ceo_user.hashed_password):
                        print("✅ Contraseña CEO: Verificada")
                    else:
                        print("❌ Contraseña CEO: No coincide")
                        
                else:
                    print("❌ Usuario CEO no encontrado")
                    print("🔧 Creando usuario CEO...")
                    
                    # Crear usuario CEO
                    hashed_password = pwd_context.hash(ceo_password)
                    new_ceo = User(
                        email=ceo_email,
                        hashed_password=hashed_password,
                        full_name="Chief Executive Officer",
                        role="CEO",
                        is_active=True,
                        is_superuser=True,
                        phone="+57 300 123 4567"
                    )
                    
                    session.add(new_ceo)
                    await session.commit()
                    await session.refresh(new_ceo)
                    
                    print("✅ Usuario CEO creado exitosamente")
                    print(f"   - ID: {new_ceo.id}")
                    print(f"   - Email: {new_ceo.email}")
                    print(f"   - Role: {new_ceo.role}")
                    
            except Exception as e:
                print(f"❌ Error verificando/creando usuario CEO: {e}")
                return False
            
            # 4. Verificar cantidad total de usuarios
            try:
                stmt = select(User)
                result = await session.execute(stmt)
                all_users = result.scalars().all()
                
                print(f"📊 Total de usuarios en el sistema: {len(all_users)}")
                
                for user in all_users:
                    print(f"   - {user.email} ({user.role}) - Activo: {user.is_active}")
                    
            except Exception as e:
                print(f"⚠️  Error listando usuarios: {e}")
            
        print("\n🎯 Verificación completada")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de estar en el entorno virtual del backend")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verify_environment():
    """Verificar variables de entorno"""
    
    print("🌍 Verificando variables de entorno...")
    
    env_vars = [
        "DATABASE_URL",
        "CEO_USER", 
        "CEO_USER_PASSWORD",
        "SECRET_KEY",
        "ENVIRONMENT"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Ocultar valores sensibles
            if "PASSWORD" in var or "SECRET" in var:
                display_value = "*" * 8
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: No configurada")

def main():
    """Función principal"""
    
    print("👑 GENIUS INDUSTRIES - Verificación de Usuario CEO")
    print("=" * 60)
    
    # Verificar variables de entorno
    verify_environment()
    print()
    
    # Verificar usuario CEO
    result = asyncio.run(verify_ceo_user())
    
    print("=" * 60)
    if result:
        print("🎉 ¡Usuario CEO verificado y configurado correctamente!")
        print(f"🔐 Acceso: {os.getenv('CEO_USER', 'ceo@geniusindustries.org')}")
        print("🌐 Dominios:")
        print("   - Frontend: geniusindustries.org")
        print("   - Backend: api.geniusindustries.org")
    else:
        print("⚠️  Hay problemas con la configuración del usuario CEO")
        print("💡 Revisa los logs anteriores para más detalles")
        sys.exit(1)

if __name__ == "__main__":
    main() 