import os
from app import create_app, db
from sqlalchemy import text

app = create_app()

print("="*50)
print("🔍 資料庫連線診斷")
print("="*50)

with app.app_context():
    # 1. 顯示目前 Flask 認為的資料庫在哪
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"📂 應用程式設定的資料庫路徑 (URI): {db_uri}")
    
    # 嘗試解析絕對路徑 (如果是 SQLite)
    if db_uri and 'sqlite' in db_uri:
        try:
            # 移除 sqlite:/// 前綴
            db_path = db_uri.replace('sqlite:///', '')
            abs_path = os.path.abspath(db_path)
            print(f"📍 資料庫檔案絕對路徑: {abs_path}")
            if os.path.exists(db_path):
                print(f"✅ 檔案確實存在")
            else:
                print(f"❌ 警告：找不到此路徑的檔案！")
        except:
            pass

    print("-" * 50)
    print("🕵️‍♂️ 檢查 skills_info 表格欄位...")
    
    with db.engine.connect() as conn:
        # 取得欄位資訊
        columns_info = conn.execute(text("PRAGMA table_info(skills_info)")).fetchall()
        # columns_info 格式通常是 (id, name, type, notnull, dflt_value, pk)
        existing_columns = [row[1] for row in columns_info]
        
        print(f"📋 目前欄位清單: {existing_columns}")
        
        # 檢查缺少的欄位
        needed_columns = ['suggested_prompt_1', 'suggested_prompt_2', 'suggested_prompt_3']
        missing_columns = [col for col in needed_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"⚠️ 發現缺少欄位: {missing_columns}，正在修復...")
            try:
                # SQLite 在一個事務中執行 DDL 可能會有問題，但這裡的 ALTER TABLE 通常是安全的
                trans = conn.begin()
                for col in missing_columns:
                    print(f"   ➕ 正在新增 {col}...")
                    conn.execute(text(f"ALTER TABLE skills_info ADD COLUMN {col} TEXT"))
                trans.commit()
                print("✅ 修復完成！")
            except Exception as e:
                print(f"❌ 修復失敗: {e}")
                trans.rollback()
        else:
            print("✅ 檢查通過：所有 AI 提示詞欄位都已存在。")

print("="*50)