#!/usr/bin/env python3
"""
🔍 Verificación de Usuario CEO en Clerk - GENIUS INDUSTRIES
Script para verificar que el usuario CEO esté registrado en Clerk
"""

import os
import sys
import requests
from pathlib import Path

def load_environment():
    """Cargar variables de entorno desde .env"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def verify_clerk_configuration():
    """Verificar configuración de Clerk"""
    print("🔑 Verificando configuración de Clerk...")
    
    # Variables necesarias
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    clerk_publishable = os.getenv("CLERK_PUBLISHABLE_KEY")
    ceo_email = os.getenv("CEO_USER", "ceo@geniusindustries.org")
    
    if not clerk_secret:
        print("❌ CLERK_SECRET_KEY no está configurada")
        return False
        
    if not clerk_publishable:
        print("❌ CLERK_PUBLISHABLE_KEY no está configurada")
        return False
        
    print(f"✅ CLERK_SECRET_KEY: {clerk_secret[:20]}...")
    print(f"✅ CLERK_PUBLISHABLE_KEY: {clerk_publishable[:20]}...")
    print(f"📧 Email CEO a verificar: {ceo_email}")
    
    return True

def search_clerk_users(email):
    """Buscar usuario en Clerk por email"""
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    
    headers = {
        "Authorization": f"Bearer {clerk_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        # Buscar usuarios en Clerk
        url = "https://api.clerk.com/v1/users"
        params = {
            "email_address": [email],
            "limit": 10
        }
        
        print(f"🔍 Buscando usuario {email} en Clerk...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Búsqueda exitosa. Encontrados {len(users)} usuarios")
            
            for user in users:
                print(f"   - Usuario ID: {user.get('id')}")
                print(f"   - Email: {user.get('email_addresses', [{}])[0].get('email_address', 'N/A')}")
                print(f"   - Nombre: {user.get('first_name')} {user.get('last_name')}")
                print(f"   - Activo: {not user.get('banned')}")
                print(f"   - Creado: {user.get('created_at')}")
                
                # Verificar si es el CEO
                emails = [addr.get('email_address') for addr in user.get('email_addresses', [])]
                if email in emails:
                    print(f"✅ Usuario CEO encontrado en Clerk!")
                    return user
                    
            if len(users) == 0:
                print(f"❌ Usuario {email} no encontrado en Clerk")
                return None
                
        else:
            print(f"❌ Error al buscar en Clerk: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión con Clerk: {e}")
        return None

def create_clerk_user(email, password, first_name, last_name):
    """Crear usuario en Clerk"""
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    
    headers = {
        "Authorization": f"Bearer {clerk_secret}",
        "Content-Type": "application/json"
    }
    
    data = {
        "email_address": [email],
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": "ceo_genius",
        "phone_number": ["+573001234567"],
        "skip_password_requirement": False,
        "skip_password_checks": False,
        "public_metadata": {
            "role": "CEO"
        },
        "private_metadata": {
            "is_superuser": True,
            "is_admin": True
        }
    }
    
    try:
        url = "https://api.clerk.com/v1/users"
        print(f"🔧 Creando usuario CEO en Clerk...")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Usuario CEO creado exitosamente en Clerk!")
            print(f"   - Usuario ID: {user.get('id')}")
            print(f"   - Email: {user.get('email_addresses', [{}])[0].get('email_address', 'N/A')}")
            return user
        else:
            print(f"❌ Error al crear usuario en Clerk: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error al crear usuario en Clerk: {e}")
        return None

def verify_clerk_access():
    """Verificar acceso básico a la API de Clerk"""
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    
    headers = {
        "Authorization": f"Bearer {clerk_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        url = "https://api.clerk.com/v1/jwks"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Conexión exitosa con API de Clerk")
            return True
        else:
            print(f"❌ Error de autenticación con Clerk: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión con Clerk: {e}")
        return False

def main():
    """Función principal"""
    print("👑 GENIUS INDUSTRIES - Verificación de Usuario CEO en Clerk")
    print("=" * 70)
    
    # Cargar variables de entorno
    load_environment()
    
    # Verificar configuración
    if not verify_clerk_configuration():
        print("⚠️  Configuración de Clerk incompleta")
        sys.exit(1)
    
    # Verificar acceso a Clerk
    if not verify_clerk_access():
        print("⚠️  No se puede conectar a Clerk")
        sys.exit(1)
    
    # Configuración del CEO
    ceo_email = os.getenv("CEO_USER", "ceo@geniusindustries.org")
    ceo_password = os.getenv("CEO_USER_PASSWORD", "GeniusCEO2025!")
    
    # Buscar usuario CEO
    ceo_user = search_clerk_users(ceo_email)
    
    if ceo_user:
        print("\n🎉 ¡Usuario CEO encontrado y configurado en Clerk!")
        print(f"🔐 Puede iniciar sesión con: {ceo_email}")
        print("🌐 URL de acceso: http://localhost:5173/admin")
        
        # Verificar metadatos
        public_metadata = ceo_user.get('public_metadata', {})
        private_metadata = ceo_user.get('private_metadata', {})
        
        print(f"👤 Rol público: {public_metadata.get('role', 'No definido')}")
        print(f"🔒 Es superuser: {private_metadata.get('is_superuser', False)}")
        
    else:
        print(f"\n❌ Usuario CEO no encontrado en Clerk")
        create_user = input("¿Deseas crear el usuario CEO en Clerk? (s/N): ").lower()
        
        if create_user == 's':
            new_user = create_clerk_user(
                email=ceo_email,
                password=ceo_password,
                first_name="Chief Executive",
                last_name="Officer"
            )
            
            if new_user:
                print("\n🎉 ¡Usuario CEO creado exitosamente!")
                print(f"🔐 Puede iniciar sesión con: {ceo_email}")
                print("🌐 URL de acceso: http://localhost:5173/admin")
            else:
                print("⚠️  No se pudo crear el usuario CEO")
                sys.exit(1)
        else:
            print("⚠️  Sin usuario CEO en Clerk, no se puede autenticar")
            sys.exit(1)
    
    print("=" * 70)
    print("🔗 Pasos siguientes:")
    print("1. Abrir http://localhost:5173")
    print("2. Hacer clic en 'Sign In'")
    print(f"3. Usar email: {ceo_email}")
    print(f"4. Usar password: {ceo_password}")
    print("5. Acceder al área de admin")

if __name__ == "__main__":
    main() 