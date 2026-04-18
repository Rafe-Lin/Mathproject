"""列出資料庫中的所有表格"""
import sqlite3

conn = sqlite3.connect('instance/kumon_math.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print("資料庫中的表格：")
for t in tables:
    print(f"  - {t[0]}")
conn.close()
