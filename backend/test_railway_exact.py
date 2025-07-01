import psycopg2
from urllib.parse import urlparse

print("🎯 TESTING RAILWAY EXACT DATABASE_PUBLIC_URL")
print("=" * 60)

# Exact URL from railway variables
DATABASE_PUBLIC_URL = "postgresql://postgres:KhloeMF0911$@trolley.proxy.rlwy.net:47731/railway"

print(f"🔗 Using exact Railway URL: {DATABASE_PUBLIC_URL}")

# Parse URL
parsed = urlparse(DATABASE_PUBLIC_URL)
print(f"🌐 Host: {parsed.hostname}")
print(f"🚪 Port: {parsed.port}")
print(f"📂 Database: {parsed.path[1:]}")  # Remove leading /
print(f"👤 User: {parsed.username}")
print(f"🔒 Password: {'*' * len(parsed.password)}")

try:
    print(f"\n🔄 Connecting with exact Railway URL...")
    
    # Connect using exact URL
    conn = psycopg2.connect(DATABASE_PUBLIC_URL, connect_timeout=15)
    
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version(), current_database(), current_user, inet_server_addr(), inet_server_port()")
    result = cursor.fetchone()
    
    print(f"✅ CONNECTION SUCCESSFUL!")
    print(f"📊 PostgreSQL: {result[0][:60]}...")
    print(f"📂 Database: {result[1]}")
    print(f"👤 User: {result[2]}")
    print(f"🌐 Server IP: {result[3]}")
    print(f"🚪 Server Port: {result[4]}")
    
    # Test table queries
    cursor.execute("""
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        LIMIT 5
    """)
    
    tables = cursor.fetchall()
    print(f"\n📋 Tables found: {len(tables)}")
    for table in tables:
        print(f"  📄 {table[0]} ({table[1]})")
    
    cursor.close()
    conn.close()
    
    print(f"\n🎉 RAILWAY CONNECTION: WORKING!")
    print(f"✅ Use DATABASE_PUBLIC_URL for external connections")
    
except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {e}")
    print(f"🔧 Error type: {type(e).__name__}")
    
    # Additional debugging
    print(f"\n🔍 DEBUGGING INFO:")
    print(f"   - Railway connect command might be interfering")
    print(f"   - Check if PostgreSQL service is running in Railway")
    print(f"   - Verify credentials in Railway dashboard")
    print(f"   - Check Railway service logs") 