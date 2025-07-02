import psycopg2
import time

print("🐳 TESTING LOCAL POSTGRESQL DOCKER")
print("=" * 50)

# Local PostgreSQL Docker Configuration
HOST = "localhost"
PORT = 5432
DATABASE = "genius_dev"
USER = "postgres"
PASSWORD = "KhloeMF0911$"

print(f"🌐 Host: {HOST}")
print(f"🚪 Port: {PORT}")
print(f"📂 Database: {DATABASE}")
print(f"👤 User: {USER}")
print(f"🔒 Password: {'*' * len(PASSWORD)}")

# Wait for container to be ready
print(f"\n⏳ Waiting for PostgreSQL container to be ready...")
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        print(f"🔄 Attempt {retry_count + 1}/{max_retries}")
        
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        
        # Test queries
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port()")
        info = cursor.fetchone()
        
        print(f"\n✅ LOCAL POSTGRESQL CONNECTION: SUCCESS!")
        print(f"📊 PostgreSQL: {version[0][:60]}...")
        print(f"📂 Database: {info[0]}")
        print(f"👤 User: {info[1]}")
        print(f"🌐 Server IP: {info[2] if info[2] else 'localhost'}")
        print(f"🚪 Server Port: {info[3]}")
        
        # Test table creation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (%s) RETURNING id", ("Test Connection",))
        test_id = cursor.fetchone()[0]
        
        # Query test data
        cursor.execute("SELECT id, name, created_at FROM test_table WHERE id = %s", (test_id,))
        test_data = cursor.fetchone()
        
        print(f"\n🧪 DATABASE OPERATIONS TEST:")
        print(f"   ✅ Table created: test_table")
        print(f"   ✅ Data inserted: ID {test_data[0]}")
        print(f"   ✅ Data retrieved: {test_data[1]}")
        print(f"   ✅ Timestamp: {test_data[2]}")
        
        # Check available extensions
        cursor.execute("SELECT name FROM pg_available_extensions WHERE name IN ('uuid-ossp', 'pgcrypto') ORDER BY name")
        extensions = cursor.fetchall()
        
        print(f"\n🔧 AVAILABLE EXTENSIONS:")
        for ext in extensions:
            print(f"   📦 {ext[0]}")
        
        # Clean up test
        cursor.execute("DROP TABLE test_table")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 LOCAL POSTGRESQL: FULLY FUNCTIONAL!")
        print(f"💡 Use this configuration for development:")
        print(f"   DATABASE_URL=postgresql://postgres:KhloeMF0911$@localhost:5432/genius_dev")
        
        break
        
    except psycopg2.OperationalError as e:
        if "could not connect" in str(e) or "timeout" in str(e):
            retry_count += 1
            if retry_count < max_retries:
                print(f"   ⏳ Container not ready yet, waiting 2 seconds...")
                time.sleep(2)
            else:
                print(f"\n❌ TIMEOUT: Container not ready after {max_retries} attempts")
                print(f"🔧 Check container status: docker ps")
                break
        else:
            print(f"\n❌ CONNECTION ERROR: {e}")
            break
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        break 