from database import get_db_connection

try:
    conn = get_db_connection()

    print("✅ Connected to MySQL Successfully!")

    cursor = conn.cursor()

    cursor.execute("SELECT DATABASE();")

    db = cursor.fetchone()

    print("Current Database:", db)

    conn.close()

except Exception as e:
    print("❌ Error:", e)