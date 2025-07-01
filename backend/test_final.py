#!/usr/bin/env python3
import psycopg2

print("🚀 GENIUS INDUSTRIES - PostgreSQL Local Test")

try:
    # Connect to local PostgreSQL
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="genius_dev",
        user="postgres",
        password="dev_password_123",
        connect_timeout=5
    )
    
    cursor = conn.cursor()
    
    # Test basic queries
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    
    cursor.execute("SELECT current_database(), current_user")
    db_info = cursor.fetchone()
    
    print(f"✅ Connection: SUCCESS")
    print(f"📊 PostgreSQL: {version[:50]}...")
    print(f"📂 Database: {db_info[0]}")
    print(f"👤 User: {db_info[1]}")
    
    # Test table operations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genius_test (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("INSERT INTO genius_test (name) VALUES (%s) RETURNING id", ("Local PostgreSQL Test",))
    test_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM genius_test WHERE id = %s", (test_id,))
    result = cursor.fetchone()
    
    print(f"🧪 Table Test: ID {result[0]}, Name: {result[1]}")
    
    # Cleanup
    cursor.execute("DROP TABLE genius_test")
    conn.commit()
    
    cursor.close()
    conn.close()
    
    print(f"🎉 LOCAL POSTGRESQL: READY FOR DEVELOPMENT!")
    print(f"🔗 Connection String: postgresql://postgres:dev_password_123@127.0.0.1:5432/genius_dev")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"🔧 Make sure Docker container is running: docker ps | findstr postgres") 