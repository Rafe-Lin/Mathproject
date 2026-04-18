import sqlite3
import os
import sys

# 設定 UTF-8 輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_database():
    """分析 kumon_math.db 資料庫的結構"""
    
    db_path = os.path.join('instance', 'kumon_math.db')
    
    if not os.path.exists(db_path):
        print(f"[X] 資料庫檔案不存在: {os.path.abspath(db_path)}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("kumon_math.db 資料庫分析報告")
    print("=" * 60)
    print(f"\n[資料庫位置] {os.path.abspath(db_path)}")
    
    # 取得檔案大小
    file_size = os.path.getsize(db_path)
    print(f"[檔案大小] {file_size:,} bytes ({file_size/1024:.2f} KB)")
    
    # 取得所有表格
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n[表格總數] 資料庫中共有 {len(tables)} 個表格:\n")
    
    # 分析每個表格
    for i, (table_name,) in enumerate(tables, 1):
        print(f"{i}. {table_name}")
        
        # 取得表格結構
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # 取得資料筆數
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"   |- 欄位數: {len(columns)}")
        print(f"   |- 資料筆數: {count}")
        print(f"   '- 欄位列表:")
        
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            pk_mark = " [PK]" if is_pk else ""
            null_mark = " NOT NULL" if not_null else ""
            print(f"      * {col_name}: {col_type}{pk_mark}{null_mark}")
        
        print()
    
    # 檢查是否有 textbook_examples 表格
    table_names = [t[0] for t in tables]
    print("=" * 60)
    print("[特別檢查]")
    print("=" * 60)
    
    if 'textbook_examples' in table_names:
        print("[V] textbook_examples 表格已存在")
        cursor.execute("SELECT COUNT(*) FROM textbook_examples")
        count = cursor.fetchone()[0]
        print(f"    資料筆數: {count}")
    else:
        print("[!] textbook_examples 表格不存在")
        print("    請執行 'python app.py' 來建立此表格")
    
    print()
    
    conn.close()

if __name__ == '__main__':
    analyze_database()

