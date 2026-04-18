import sqlite3

# 連接正確的資料庫
conn = sqlite3.connect('instance/math_master.db')
cursor = conn.cursor()

# 列出所有資料表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== instance/math_master.db 中的所有資料表 ===\n")
if tables:
    for table in tables:
        table_name = table[0]
        print(f"[{table_name}]")
        
        # 顯示資料筆數
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  資料筆數: {count}")
        
        # 顯示欄位結構
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"  欄位: {', '.join([col[1] for col in columns[:5]])}", end='')
        if len(columns) > 5:
            print(f" ... (共 {len(columns)} 個欄位)")
        else:
            print()
        print()
else:
    print("資料庫中沒有任何資料表!")

# 特別檢查 skill_curriculum
print("\n=== 檢查課程相關資料表 ===")
for table_name in ['skill_curriculum', 'skills_info', 'SkillCurriculum', 'SkillInfo']:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    if result:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"[OK] {table_name} 存在 (資料筆數: {count})")
        
        # 如果是課程表,顯示範例資料
        if 'curriculum' in table_name.lower():
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                samples = cursor.fetchall()
                if samples:
                    # 取得欄位名稱
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    col_names = [col[1] for col in cursor.fetchall()]
                    print(f"  欄位: {col_names}")
                    print(f"  範例資料:")
                    for sample in samples:
                        print(f"    {sample[:5]}...")  # 只顯示前5個欄位
            except Exception as e:
                print(f"  無法讀取範例資料: {e}")

conn.close()
