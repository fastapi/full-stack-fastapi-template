import psycopg2
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="genius_dev",
        user="postgres", 
        password="dev_password_123"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 'SUCCESS!' as result")
    result = cursor.fetchone()
    print(f"✅ PostgreSQL Local: {result[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}") 