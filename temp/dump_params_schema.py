import sqlite3
import os

db_path = r"D:\Python\Mathproject\instance\kumon_math.db"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"-- Schema extraction from {db_path}")
    cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name;")
    results = cursor.fetchall()
    
    for type_, name, sql in results:
        print(f"\n-- {type_}: {name}")
        print(f"{sql};")
        
    conn.close()
except Exception as e:
    print(f"Error extracting schema: {e}")
