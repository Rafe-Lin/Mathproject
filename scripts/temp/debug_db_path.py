# scripts/debug_db_path.py
import sys
import os
from sqlalchemy import text

# 設定路徑以匯入主程式
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import ExperimentLog

def check_db_status():
    print(f"🔍 [診斷模式] 資料庫檢查工具")
    
    with app.app_context():
        # 1. 檢查資料庫連線路徑
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"📂 目前連線的資料庫 URI: {db_uri}")
        
        # 2. 嘗試找出實際檔案路徑 (針對 SQLite)
        if db_uri and 'sqlite:///' in db_uri:
            # 移除前綴，取得相對路徑
            rel_path = db_uri.replace('sqlite:///', '')
            abs_path = os.path.abspath(rel_path)
            # 如果是 instance folder 結構
            if not os.path.exists(rel_path) and 'instance' not in rel_path:
                 # 嘗試檢查 instance 資料夾
                 instance_path = os.path.join(app.instance_path, os.path.basename(rel_path))
                 if os.path.exists(instance_path):
                     print(f"⚠️  注意：Flask 預設可能指向 instance 資料夾: {instance_path}")
                     print(f"    但目前設定指向: {abs_path}")
            
            print(f"📄 資料庫檔案絕對路徑: {abs_path}")
            if os.path.exists(abs_path):
                size = os.path.getsize(abs_path) / 1024  # KB
                print(f"    -> 檔案存在 (大小: {size:.2f} KB)")
            else:
                print(f"    -> ❌ 檔案不存在！您的腳本可能連到了一個空氣資料庫。")

        # 3. 查詢最近的 ExperimentLog
        print("\n📊 正在查詢最近 5 筆實驗紀錄...")
        try:
            # 使用原生 SQL 以避開可能的 ORM 快取
            sql = text("SELECT id, skill_id, model_name, timestamp, is_success FROM experiment_log ORDER BY id DESC LIMIT 5")
            result = db.session.execute(sql)
            rows = result.fetchall()
            
            if not rows:
                print("❌ 資料庫是空的！沒有任何實驗紀錄。")
            else:
                for row in rows:
                    # row 格式: (id, skill_id, model_name, timestamp, is_success)
                    print(f"   ID: {row[0]} | 時間: {row[3]} | 模型: {row[2]} | Skill: {row[1]}")
                    
        except Exception as e:
            print(f"❌ 查詢失敗: {e}")

if __name__ == "__main__":
    check_db_status()