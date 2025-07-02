#!/usr/bin/env python3
"""
VERIFICACIÓN UNIFICADA - GENIUS INDUSTRIES
Verifica que ambas bases de datos (local y Railway) usen la misma contraseña
"""

import sys
import requests
import asyncio
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

try:
    import asyncpg
    import psycopg2
    from sqlalchemy import create_engine, text
except ImportError as e:
    print(f"❌ Error importing libraries: {e}")
    print("Install with: pip install asyncpg psycopg2-binary sqlalchemy")
    sys.exit(1)

# CONFIGURACIÓN UNIFICADA
UNIFIED_PASSWORD = "KhloeMF0911$"

LOCAL_CONFIG = {
    "name": "PostgreSQL Local",
    "host": "localhost",
    "port": 5432,
    "database": "genius_dev",
    "user": "postgres",
    "password": UNIFIED_PASSWORD
}

RAILWAY_CONFIG = {
    "name": "Railway PostgreSQL",
    "host": "postgres-production-bff4.up.railway.app",
    "port": 5432,
    "database": "railway",
    "user": "postgres",
    "password": UNIFIED_PASSWORD
}

def test_psycopg2_connection(config):
    """Test con psycopg2"""
    try:
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            sslmode="require" if "railway" in config["host"] else "disable",
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version(), current_database(), current_user")
        result = cursor.fetchone()
        
        # Test tabla users si existe
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
        except:
            user_count = "N/A (tabla no existe)"
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "version": result[0].split()[1],
            "database": result[1],
            "user": result[2],
            "user_count": user_count
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_sqlalchemy_connection(config):
    """Test con SQLAlchemy (usado en FastAPI)"""
    try:
        # Construir URL de conexión
        if "railway" in config["host"]:
            database_url = f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode=require"
        else:
            database_url = f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode=disable"
        
        engine = create_engine(database_url, pool_timeout=10)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            
            # Test tablas
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in tables_result.fetchall()]
        
        engine.dispose()
        
        return {
            "success": True,
            "version": result[0].split()[1],
            "tables": tables,
            "table_count": len(tables)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_backend_api():
    """Test de API del backend"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "message": response.json().get("message", "")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Función principal de verificación"""
    print("🏢 GENIUS INDUSTRIES - VERIFICACIÓN UNIFICADA")
    print("=" * 65)
    print(f"🔐 Contraseña Unificada: {'*' * len(UNIFIED_PASSWORD)}")
    print("=" * 65)
    
    results = {}
    
    # Test Local PostgreSQL
    print(f"\n🗄️ PROBANDO: {LOCAL_CONFIG['name']}")
    print(f"   🌐 Host: {LOCAL_CONFIG['host']}:{LOCAL_CONFIG['port']}")
    print(f"   📂 Database: {LOCAL_CONFIG['database']}")
    
    psycopg2_local = test_psycopg2_connection(LOCAL_CONFIG)
    sqlalchemy_local = test_sqlalchemy_connection(LOCAL_CONFIG)
    
    if psycopg2_local["success"]:
        print(f"   ✅ psycopg2: OK - PostgreSQL {psycopg2_local['version']}")
        print(f"   👥 Usuarios en DB: {psycopg2_local['user_count']}")
    else:
        print(f"   ❌ psycopg2: {psycopg2_local['error']}")
    
    if sqlalchemy_local["success"]:
        print(f"   ✅ SQLAlchemy: OK - {sqlalchemy_local['table_count']} tablas")
        if sqlalchemy_local['tables']:
            print(f"   🗂️ Tablas: {', '.join(sqlalchemy_local['tables'][:5])}")
    else:
        print(f"   ❌ SQLAlchemy: {sqlalchemy_local['error']}")
    
    results['local'] = psycopg2_local["success"] and sqlalchemy_local["success"]
    
    # Test Railway PostgreSQL  
    print(f"\n🚂 PROBANDO: {RAILWAY_CONFIG['name']}")
    print(f"   🌐 Host: {RAILWAY_CONFIG['host']}:{RAILWAY_CONFIG['port']}")
    print(f"   📂 Database: {RAILWAY_CONFIG['database']}")
    
    psycopg2_railway = test_psycopg2_connection(RAILWAY_CONFIG)
    sqlalchemy_railway = test_sqlalchemy_connection(RAILWAY_CONFIG)
    
    if psycopg2_railway["success"]:
        print(f"   ✅ psycopg2: OK - PostgreSQL {psycopg2_railway['version']}")
        print(f"   👥 Usuarios en DB: {psycopg2_railway['user_count']}")
    else:
        print(f"   ❌ psycopg2: {psycopg2_railway['error']}")
    
    if sqlalchemy_railway["success"]:
        print(f"   ✅ SQLAlchemy: OK - {sqlalchemy_railway['table_count']} tablas")
        if sqlalchemy_railway['tables']:
            print(f"   🗂️ Tablas: {', '.join(sqlalchemy_railway['tables'][:5])}")
    else:
        print(f"   ❌ SQLAlchemy: {sqlalchemy_railway['error']}")
    
    results['railway'] = psycopg2_railway["success"] and sqlalchemy_railway["success"]
    
    # Test Backend API
    print(f"\n🌐 PROBANDO: Backend API")
    backend_result = test_backend_api()
    
    if backend_result["success"]:
        print(f"   ✅ API: OK - {backend_result['message']}")
    else:
        print(f"   ❌ API: {backend_result['error']}")
    
    results['backend'] = backend_result["success"]
    
    # Resumen Final
    print("\n" + "=" * 65)
    print("📊 RESUMEN FINAL:")
    print(f"   🗄️ Base de datos LOCAL: {'✅ FUNCIONANDO' if results['local'] else '❌ ERROR'}")
    print(f"   🚂 Base de datos RAILWAY: {'✅ FUNCIONANDO' if results['railway'] else '❌ ERROR'}")
    print(f"   🌐 Backend API: {'✅ FUNCIONANDO' if results['backend'] else '❌ ERROR'}")
    
    if results['local']:
        print(f"\n🎉 LOCAL DATABASE: COMPLETAMENTE FUNCIONAL")
        print(f"   📍 Configuración: postgresql://postgres:KhloeMF0911$@localhost:5432/genius_dev")
    
    if results['railway']:
        print(f"\n🎉 RAILWAY DATABASE: COMPLETAMENTE FUNCIONAL")
        print(f"   📍 Configuración: postgresql://postgres:KhloeMF0911$@postgres-production-bff4.up.railway.app:5432/railway")
    
    if not results['railway']:
        print(f"\n⚠️ RAILWAY DATABASE: No disponible")
        print(f"   💡 Posibles causas:")
        print(f"      - Instancia pausada/inactiva")
        print(f"      - Problemas de conectividad")
        print(f"      - Configuración de firewall")
        print(f"      - Dirección de host cambiada")
    
    print(f"\n🔐 CONTRASEÑA UNIFICADA CONFIGURADA: KhloeMF0911$")
    print(f"   ✅ Misma contraseña para local y producción")
    
    total_success = sum([results['local'], results.get('railway', False), results['backend']])
    print(f"\n📈 ESTADO GENERAL: {total_success}/3 servicios funcionando")
    
    if results['local'] and results['backend']:
        print(f"\n🚀 SISTEMA LISTO PARA DESARROLLO LOCAL")
    
    if results['local'] and results['railway']:
        print(f"\n🌟 SISTEMA COMPLETAMENTE FUNCIONAL (LOCAL + PRODUCCIÓN)")

if __name__ == "__main__":
    main() 