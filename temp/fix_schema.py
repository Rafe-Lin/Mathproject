# fix_schema.py
import sqlite3
import os

# --- 設定 ---
# 根據您的 config.py，Flask 會將資料庫建立在 'instance' 資料夾中
DB_PATH = os.path.join('instance', 'kumon_math.db')
TABLE_NAME = 'skills_info'
COLUMNS_TO_ADD = {
    'suggested_prompt_1': 'TEXT',
    'suggested_prompt_2': 'TEXT',
    'suggested_prompt_3': 'TEXT',
}

def fix_database_schema():
    """
    連線到 SQLite 資料庫，並為 skills_info 表格新增缺失的欄位。
    """
    if not os.path.exists(DB_PATH):
        print(f"❌ 錯誤：在 '{os.path.abspath(DB_PATH)}' 找不到資料庫檔案。")
        print("請先執行一次 app.py 來建立資料庫。")
        return

    print(f"🔗 正在連線到資料庫: {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. 取得現有欄位
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"'{TABLE_NAME}' 表格現有欄位: {existing_columns}")

        # 2. 檢查並新增缺失的欄位
        for col_name, col_type in COLUMNS_TO_ADD.items():
            if col_name not in existing_columns:
                alter_query = f"ALTER TABLE {TABLE_NAME} ADD COLUMN {col_name} {col_type}"
                print(f"  -> 欄位 '{col_name}' 不存在，正在執行: {alter_query}")
                cursor.execute(alter_query)
            else:
                print(f"  -> 欄位 '{col_name}' 已存在，無需處理。")

        # 3. 提交變更
        conn.commit()
        print("\n✅ 資料庫結構更新成功！")

    except sqlite3.Error as e:
        print(f"\n❌ 資料庫操作失敗: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("🔗 資料庫連線已關閉。")

if __name__ == "__main__":
    fix_database_schema()