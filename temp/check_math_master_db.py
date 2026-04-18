import sqlite3
import os

# 尋找資料庫檔案
db_files = ['math-master.db', 'kumon_math.db', 'math_master.db']
db_path = None

for db_file in db_files:
    if os.path.exists(db_file):
        db_path = db_file
        print(f"找到資料庫: {db_file}")
        break

if not db_path:
    print("找不到資料庫檔案!")
    exit(1)

# 連接資料庫
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 列出所有資料表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\n=== {db_path} 中的所有資料表 ===")
if tables:
    for table in tables:
        print(f"\n[{table[0]}]")
        
        # 顯示每個表的資料筆數
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  資料筆數: {count}")
        
        # 顯示欄位結構
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"  欄位: {', '.join([col[1] for col in columns])}")
else:
    print("資料庫中沒有任何資料表!")

# 特別檢查 skill_curriculum
print("\n=== 檢查 skill_curriculum 資料表 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_curriculum'")
result = cursor.fetchone()

if result:
    print("[OK] skill_curriculum 資料表存在")
    
    # 查看範例資料
    cursor.execute("SELECT curriculum, grade, volume, chapter, section, skill_id FROM skill_curriculum LIMIT 3")
    samples = cursor.fetchall()
    if samples:
        print("\n範例資料:")
        for sample in samples:
            print(f"  {sample}")
else:
    print("[ERROR] skill_curriculum 資料表不存在")

conn.close()
