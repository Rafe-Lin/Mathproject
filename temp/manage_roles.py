import os
import sys

# 將專案根目錄加入 Python 路徑，以便能正確匯入 app 和 models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User

def manage_user_roles():
    """
    一個互動式腳本，用於查看和管理使用者的角色。
    """
    # 1. 載入 Flask App Context 和 DB
    app = create_app()
    with app.app_context():
        print("--- 目前使用者列表 ---")
        
        # 2. 查詢並列出所有使用者
        try:
            users = User.query.order_by(User.id).all()
            if not users:
                print("資料庫中沒有任何使用者。")
            else:
                for user in users:
                    print(f"[{user.id}] {user.username} - 目前身分: {user.role}")
        except Exception as e:
            print(f"查詢使用者時發生錯誤: {e}")
            print("請確認資料庫連線是否正常，以及 'user' 資料表是否存在。")
            return

        print("-" * 40)

        # 3. 互動式更新
        while True:
            username_to_promote = input("\n👉 請輸入要設定為管理員的 Username (直接按 Enter 離開): ").strip()

            if not username_to_promote:
                print("👋 操作結束。")
                break

            # 4. 執行更新
            user_to_update = User.query.filter_by(username=username_to_promote).first()

            if user_to_update:
                user_to_update.role = 'teacher'
                db.session.commit()
                print(f"✅ User '{user_to_update.username}' 已升級為管理員！")
            else:
                print(f"❌ 找不到使用者: '{username_to_promote}'")

if __name__ == "__main__":
    manage_user_roles()