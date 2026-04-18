# create_missing_skill_files.py
import sys
import os
from queue import Queue
import traceback

# --- 重要提示 ---
# 此腳本在初始化應用時，需要讀取 GEMINI_API_KEY 環境變數。
# 如果執行時出現關於 GEMINI_API_KEY 的錯誤，請確保您的執行環境(例如 .env 檔案)中已正確設定此變數。
# ---

def find_and_create_missing_files():
    """
    Finds skills that exist in the database but not on the filesystem,
    and creates placeholder files for them using the code generator.
    """
    print("--- 開始檢查缺失的技能檔案 ---")
    
    # 1. 將專案根目錄加入 Python 路徑，以確保能正確 import
    sys.path.append(os.getcwd())
    
    try:
        from app import create_app
        from models import db, SkillInfo
        from core.code_generator import auto_generate_skill_code
    except ImportError as e:
        print(f"錯誤：無法導入必要的模組 - {e}")
        print("請確認您是在專案的根目錄下執行此腳本。")
        return

    # 建立 Flask app 上下文
    try:
        app = create_app()
    except ValueError as e:
        # 捕捉因環境變數缺失導致的啟動錯誤
        print(f"\n錯誤：應用程式初始化失敗。\n")
        print(f"原因：{e}")
        print("請檢查您的 .env 檔案或環境變數是否已正確設定（特別是 GEMINI_API_KEY）。\n")
        return

    with app.app_context():
        # 2. 取得資料庫中的所有技能 ID
        try:
            db_skills = {skill.skill_id for skill in db.session.query(SkillInfo.skill_id).all()}
            print(f"資料庫中總共找到 {len(db_skills)} 個技能。\n")
        except Exception as e:
            print(f"錯誤：從資料庫讀取技能列表時發生錯誤 - {e}")
            return

        # 3. 取得檔案系統中的所有技能檔案名稱
        skills_dir = os.path.join(os.getcwd(), 'skills')
        if not os.path.isdir(skills_dir):
            print(f"錯誤：找不到 'skills' 資料夾於 '{os.getcwd()}'")
            return
            
        fs_skills = {
            f.replace('.py', '') 
            for f in os.listdir(skills_dir) 
            if f.endswith('.py') and f != '__init__.py'
        }
        print(f"檔案系統中總共找到 {len(fs_skills)} 個技能檔案。\n")

        # 4. 找出差異 (存在於資料庫但不存在於檔案系統)
        missing_skills = sorted(list(db_skills - fs_skills))

        if not missing_skills:
            print("\n恭喜！沒有發現任何缺失的技能檔案。\n")
            return

        print(f"\n發現 {len(missing_skills)} 個缺失的技能檔案，現在開始生成...\n")
        
        # 用於接收生成過程中的日誌訊息
        log_queue = Queue()
        files_created = 0
        files_failed = 0

        # 5. 為每一個缺失的技能呼叫程式碼生成器
        for skill_id in missing_skills:
            try:
                print(f"  - 正在生成: {skill_id}.py ... ", end="")
                success, message = auto_generate_skill_code(skill_id, log_queue)
                if success:
                    print("成功！\n")
                    files_created += 1
                else:
                    print(f"失敗！原因: {message}\n")
                    files_failed += 1
            except Exception as e:
                print(f"生成過程中發生未預期錯誤: {e}\n")
                traceback.print_exc()
                files_failed += 1
        
        print("\n--- 任務完成 ---")
        print(f"成功創建 {files_created} 個檔案。\n")
        if files_failed > 0:
            print(f"有 {files_failed} 個檔案生成失敗，請檢查上面的錯誤訊息。\n")

if __name__ == '__main__':
    find_and_create_missing_files()
