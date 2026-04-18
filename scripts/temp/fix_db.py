import os
import sys

# 1. 將專案根目錄 (上一層) 加入 Python 搜尋路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 2. 現在可以正常匯入了
from app import create_app
from models import db

app = create_app()

with app.app_context():
    print(f"🔧 Target DB: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')}")
    print("正在檢查並建立缺失的資料表...")
    db.create_all()
    print("✅ 資料庫修復完成！所有表 (包含 quiz_attempts) 都已就緒。")