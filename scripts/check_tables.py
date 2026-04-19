import os
import sys

# 1. 取得當前檔案所在的目錄 (scripts/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 取得上一層目錄 (專案根目錄)
project_root = os.path.dirname(current_dir)
# 3. 將專案根目錄加入 Python 搜尋路徑
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 4. 現在可以正確匯入了
from app import create_app
from models import db

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print("\n" + "="*50)
    print(f"📊 資料庫現有的資料表清單 ({len(tables)} 個):")
    print("="*50)
    for i, table in enumerate(sorted(tables), 1):
        print(f"   [{i}] {table}")
    print("="*50 + "\n")
    
    # 特別檢查目標表
    target = 'skill_gencode_prompt'
    if target in tables:
        print(f"✅ 確認：資料表 '{target}' 存在於資料庫中。")
    else:
        print(f"❌ 警告：找不到資料表 '{target}'！請執行 fix_db.py 建立它。")