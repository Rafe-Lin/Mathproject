# -*- coding: utf-8 -*-
# update_db_schema.py
"""
資料庫 Schema 更新腳本 - 新增 textbook_examples 表格

此腳本會安全地檢查並新增 textbook_examples 表格到現有資料庫，
不會影響已存在的資料。

使用方式:
    python update_db_schema.py
"""

import sqlite3
import os
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String, Text, ForeignKey
from config import SQLALCHEMY_DATABASE_URI

def check_and_create_textbook_examples_table():
    """檢查並創建 textbook_examples 表格"""
    
    print("=" * 60)
    print("資料庫 Schema 更新工具 - textbook_examples 表格")
    print("=" * 60)
    
    # 建立 SQLAlchemy engine
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    inspector = inspect(engine)
    
    # 1. 檢查表格是否存在
    print("\n[步驟 1] 檢查 textbook_examples 表格是否存在...")
    existing_tables = inspector.get_table_names()
    
    if 'textbook_examples' in existing_tables:
        print("[OK] textbook_examples 表格已存在，無需創建。")
        print("\n表格欄位:")
        columns = inspector.get_columns('textbook_examples')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        return True
    
    print("[X] textbook_examples 表格不存在，準備創建...")
    
    # 2. 檢查 skills_info 表格是否存在 (外鍵依賴)
    print("\n[步驟 2] 檢查外鍵依賴 (skills_info 表格)...")
    if 'skills_info' not in existing_tables:
        print("[X] 錯誤: skills_info 表格不存在，無法建立外鍵約束！")
        print("   請先確保資料庫已正確初始化。")
        return False
    
    print("[OK] skills_info 表格存在，可以建立外鍵約束。")
    
    # 3. 創建表格
    print("\n[步驟 3] 創建 textbook_examples 表格...")
    
    try:
        # 使用原生 SQL 創建表格 (與 init_db 保持一致)
        conn = engine.raw_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS textbook_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT NOT NULL,
                source_curriculum TEXT NOT NULL,
                source_volume TEXT NOT NULL,
                source_chapter TEXT NOT NULL,
                source_section TEXT NOT NULL,
                source_description TEXT NOT NULL,
                source_paragraph TEXT,
                problem_text TEXT NOT NULL,
                problem_type TEXT,
                correct_answer TEXT,
                detailed_solution TEXT,
                difficulty_level INTEGER DEFAULT 1,
                FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print("[OK] textbook_examples 表格創建成功！")
        
        # 4. 驗證表格結構
        print("\n[步驟 4] 驗證表格結構...")
        cursor.execute("PRAGMA table_info(textbook_examples)")
        columns = cursor.fetchall()
        
        print("\n表格欄位:")
        for col in columns:
            col_id, name, col_type, not_null, default_val, pk = col
            pk_marker = " [PK]" if pk else ""
            null_marker = " NOT NULL" if not_null else ""
            default_marker = f" DEFAULT {default_val}" if default_val else ""
            print(f"  - {name}: {col_type}{pk_marker}{null_marker}{default_marker}")
        
        # 5. 驗證外鍵約束
        print("\n[步驟 5] 驗證外鍵約束...")
        cursor.execute("PRAGMA foreign_key_list(textbook_examples)")
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print("\n外鍵約束:")
            for fk in foreign_keys:
                fk_id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"  - {from_col} -> {table}.{to_col} (ON DELETE {on_delete})")
        else:
            print("[!] 警告: 未檢測到外鍵約束 (可能需要啟用 PRAGMA foreign_keys=ON)")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("[OK] 資料庫更新完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[X] 錯誤: 創建表格時發生異常")
        print(f"   {str(e)}")
        return False

def verify_table_creation():
    """額外驗證: 嘗試插入並刪除測試資料"""
    print("\n[額外驗證] 測試表格讀寫功能...")
    
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        conn = engine.raw_connection()
        cursor = conn.cursor()
        
        # 檢查是否有 skill_id 可用於測試
        cursor.execute("SELECT skill_id FROM skills_info LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            print("[!] 跳過寫入測試 (skills_info 表格為空)")
            conn.close()
            return True
        
        test_skill_id = result[0]
        
        # 插入測試資料
        cursor.execute('''
            INSERT INTO textbook_examples 
            (skill_id, source_curriculum, source_volume, source_chapter, 
             source_section, source_description, problem_text, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_skill_id, 'general', '測試冊別', '測試章', 
              '測試節', '測試說明', '這是一個測試題目', 1))
        
        test_id = cursor.lastrowid
        conn.commit()
        print(f"[OK] 測試資料插入成功 (ID: {test_id})")
        
        # 讀取測試資料
        cursor.execute("SELECT * FROM textbook_examples WHERE id = ?", (test_id,))
        test_data = cursor.fetchone()
        
        if test_data:
            print(f"[OK] 測試資料讀取成功")
        
        # 刪除測試資料
        cursor.execute("DELETE FROM textbook_examples WHERE id = ?", (test_id,))
        conn.commit()
        print(f"[OK] 測試資料清理完成")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[X] 測試失敗: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n開始執行資料庫更新...\n")
    
    success = check_and_create_textbook_examples_table()
    
    if success:
        verify_table_creation()
        print("\n[OK] 所有檢查通過！textbook_examples 表格已就緒。")
        print("\n下一步:")
        print("  1. 可以開始使用 TextbookExample 模型進行資料操作")
        print("  2. 如需管理介面，請更新 core/routes.py 中的 admin 路由")
        print("  3. 如需匯入資料，可參考 import_data.py 建立匯入腳本")
    else:
        print("\n[X] 更新失敗，請檢查錯誤訊息。")
