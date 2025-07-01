import psycopg2
import os
from pathlib import Path

print("🚂 TESTING RAILWAY POSTGRESQL - FIXED CONFIGURATION")
print("=" * 60)

# Railway CORRECTED Configuration
HOST = "trolley.proxy.rlwy.net"  # Railway proxy host
PORT = 47731  # Railway proxy port (not 5432!)
DATABASE = "railway"
USER = "postgres"
PASSWORD = "KhloeMF0911$"

print(f"🌐 Host: {HOST}")
print(f"🚪 Port: {PORT} (Railway Proxy)")
print(f"📂 Database: {DATABASE}")
print(f"👤 User: {USER}")
print(f"🔒 Password: {'*' * len(PASSWORD)}")

# Test both configurations
configs = [
    {
        "name": "Railway Proxy (CORRECTO)",
        "host": "trolley.proxy.rlwy.net",
        "port": 47731,
        "sslmode": "require"
    },
    {
        "name": "Railway Internal (PARA DOCKER)",
        "host": "postgres.railway.internal", 
        "port": 5432,
        "sslmode": "require"
    },
    {
        "name": "Railway Public Domain (BACKUP)",
        "host": "postgres-production-bff4.up.railway.app",
        "port": 5432,
        "sslmode": "require"
    }
]

successful_config = None

for config in configs:
    try:
        print(f"\n🔄 Testing: {config['name']}")
        print(f"   Host: {config['host']}:{config['port']}")
        
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            sslmode=config['sslmode'],
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version(), current_database(), current_user")
        result = cursor.fetchone()
        
        print(f"✅ SUCCESS with {config['name']}!")
        print(f"📊 PostgreSQL: {result[0][:50]}...")
        print(f"📂 Database: {result[1]}")
        print(f"👤 User: {result[2]}")
        
        # Test table access
        cursor.execute("""
            SELECT count(*) as table_count
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"📋 Tables in public schema: {table_count}")
        
        cursor.close()
        conn.close()
        
        successful_config = config
        break
        
    except Exception as e:
        print(f"❌ FAILED with {config['name']}: {e}")
        print(f"🔧 Error type: {type(e).__name__}")

if successful_config:
    print(f"\n🎉 RAILWAY POSTGRESQL CONNECTION: SUCCESS!")
    print(f"✅ Working configuration: {successful_config['name']}")
    print(f"🔗 Use: {successful_config['host']}:{successful_config['port']}")
    
    # Update recommendation
    print(f"\n📝 CONFIGURATION RECOMMENDATION:")
    print(f"POSTGRES_SERVER={successful_config['host']}")
    print(f"POSTGRES_PORT={successful_config['port']}")
    print(f"DATABASE_URL=postgresql://postgres:KhloeMF0911$@{successful_config['host']}:{successful_config['port']}/railway")
else:
    print(f"\n💥 ALL CONFIGURATIONS FAILED")
    print(f"🔧 Check Railway service status and credentials") 