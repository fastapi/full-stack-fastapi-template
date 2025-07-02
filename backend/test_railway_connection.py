#!/usr/bin/env python3
"""
Script para testear la conexión a Railway PostgreSQL
Ejecutar desde el directorio backend: python test_railway_connection.py
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Agregar el directorio padre al path para importar modules
sys.path.append(str(Path(__file__).parent))

try:
    import asyncpg
    import psycopg2
    from sqlalchemy import create_engine, text
    import psutil
except ImportError as e:
    print(f"❌ Error importing libraries: {e}")
    print("Install with: pip install asyncpg psycopg2-binary sqlalchemy psutil")
    sys.exit(1)

# Configuración Railway (actualiza con tus datos)
RAILWAY_CONFIG = {
    "host": "postgres-production-bff4.up.railway.app",
    "port": 5432,
    "database": "railway",
    "user": "postgres",
    "password": "KhloeMF0911$"  # ✅ PASSWORD ACTUALIZADO
}

DATABASE_URL = f"postgresql://{RAILWAY_CONFIG['user']}:{RAILWAY_CONFIG['password']}@{RAILWAY_CONFIG['host']}:{RAILWAY_CONFIG['port']}/{RAILWAY_CONFIG['database']}"

async def test_asyncpg_connection():
    """Test directo con asyncpg (recomendado para FastAPI)"""
    print("🔍 Testing AsyncPG connection...")
    try:
        start_time = time.time()
        conn = await asyncpg.connect(DATABASE_URL, ssl="require")
        connect_time = time.time() - start_time
        
        # Test basic query
        result = await conn.fetchrow("SELECT version(), current_database(), current_user")
        
        # Test app-specific query
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        await conn.close()
        
        print(f"✅ AsyncPG Connection OK")
        print(f"   📊 Connection time: {connect_time:.3f}s")
        print(f"   🗄️ PostgreSQL version: {result['version'].split()[1]}")
        print(f"   📁 Database: {result['current_database']}")
        print(f"   👤 User: {result['current_user']}")
        print(f"   📋 Tables found: {len(tables)}")
        
        if tables:
            table_names = [table['table_name'] for table in tables[:5]]
            print(f"   🗂️ Sample tables: {', '.join(table_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ AsyncPG Error: {e}")
        return False

def test_psycopg2_connection():
    """Test con psycopg2 (usado por SQLAlchemy)"""
    print("\n🔍 Testing psycopg2 connection...")
    try:
        start_time = time.time()
        conn = psycopg2.connect(
            host=RAILWAY_CONFIG["host"],
            port=RAILWAY_CONFIG["port"],
            database=RAILWAY_CONFIG["database"],
            user=RAILWAY_CONFIG["user"],
            password=RAILWAY_CONFIG["password"],
            sslmode="require",
            connect_timeout=30
        )
        connect_time = time.time() - start_time
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Test connection info
        cursor.execute("""
            SELECT 
                COUNT(*) as total_connections,
                COUNT(*) FILTER (WHERE state = 'active') as active_connections
            FROM pg_stat_activity
        """)
        conn_info = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"✅ psycopg2 Connection OK")
        print(f"   📊 Connection time: {connect_time:.3f}s")
        print(f"   🗄️ Version: {version.split()[1]}")
        print(f"   🔗 Total connections in server: {conn_info[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ psycopg2 Error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test con SQLAlchemy (usado en FastAPI)"""
    print("\n🔍 Testing SQLAlchemy connection...")
    try:
        # Configuración optimizada para Railway
        engine = create_engine(
            DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={
                "sslmode": "require",
                "application_name": "genius-industries-test",
                "connect_timeout": "30",
            }
        )
        
        start_time = time.time()
        with engine.connect() as conn:
            connect_time = time.time() - start_time
            
            # Test queries
            result = conn.execute(text("SELECT version()")).fetchone()
            
            # Test pool info
            pool = engine.pool
            
            print(f"✅ SQLAlchemy Connection OK")
            print(f"   📊 Connection time: {connect_time:.3f}s")
            print(f"   🗄️ Version: {result[0].split()[1]}")
            print(f"   🏊 Pool size: {pool.size()}")
            print(f"   🏊 Pool checked out: {pool.checkedout()}")
            
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy Error: {e}")
        return False

def test_latency():
    """Test de latencia a Railway"""
    print("\n🔍 Testing latency to Railway...")
    try:
        import subprocess
        import platform
        
        host = RAILWAY_CONFIG["host"]
        
        # Comando ping según OS
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "4", host]
        else:
            cmd = ["ping", "-c", "4", host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Ping to {host} successful")
            # Buscar tiempo promedio en la salida
            lines = result.stdout.split('\n')
            for line in lines:
                if 'avg' in line.lower() or 'average' in line.lower():
                    print(f"   📶 {line.strip()}")
                    break
        else:
            print(f"⚠️ Ping failed: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Latency test error: {e}")

def check_environment():
    """Verificar configuración del entorno"""
    print("🔍 Environment Check...")
    
    # Verificar variables críticas
    if RAILWAY_CONFIG["password"] == "TU_PASSWORD_AQUI":
        print("❌ CRITICAL: Update your Railway password in this script!")
        return False
    
    print(f"✅ Railway Host: {RAILWAY_CONFIG['host']}")
    print(f"✅ Railway Database: {RAILWAY_CONFIG['database']}")
    print(f"✅ Railway User: {RAILWAY_CONFIG['user']}")
    print(f"✅ Password: {'*' * len(RAILWAY_CONFIG['password'])}")
    
    return True

async def main():
    """Función principal"""
    print("🚀 GENIUS INDUSTRIES - Railway PostgreSQL Connection Test")
    print("=" * 60)
    
    # Verificar entorno
    if not check_environment():
        print("\n❌ Environment check failed. Please update configuration.")
        return
    
    # Test latencia
    test_latency()
    
    # Test conexiones
    results = []
    results.append(await test_asyncpg_connection())
    results.append(test_psycopg2_connection())
    results.append(test_sqlalchemy_connection())
    
    # Resumen
    print("\n" + "=" * 60)
    successful_tests = sum(results)
    total_tests = len(results)
    
    if successful_tests == total_tests:
        print(f"🎉 All tests passed! ({successful_tests}/{total_tests})")
        print("✅ Railway PostgreSQL is ready for production!")
    else:
        print(f"⚠️ Some tests failed ({successful_tests}/{total_tests})")
        print("❌ Please check your Railway configuration.")
    
    print("\n🔧 Next steps:")
    print("1. Update .env.production with your Railway credentials")
    print("2. Configure these variables in Dokploy environment")
    print("3. Deploy and test your application")

if __name__ == "__main__":
    asyncio.run(main()) 