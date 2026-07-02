import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@10",
        database="ai_interview_assistant"
    )

    print("✅ Connected to Database Successfully!")

    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print(cursor.fetchone())

    conn.close()

except Exception as e:
    print("❌", e)