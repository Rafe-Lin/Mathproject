import sys
import os
import pandas as pd
from sqlalchemy import text

# --- 路徑設定 ---
# 確保能找到 app 模組
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)

from app import app, db
from app.models import Question, QuizAttempt
# 如果你有 User 或其他 Model，也要在這裡 import，例如: from app.models import User

# 設定備份檔案位置 (請確認檔案名稱是否正確)
excel_file = os.path.join(project_root, "kumon_math_20260110_1810.xlsx")
db_path = os.path.join(project_root, "instance", "kumon_math.db")

def restore_all_tables():
    print(f"🚀 開始執行全資料庫還原程序...")
    print(f"📂 來源檔案: {excel_file}")

    if not os.path.exists(excel_file):
        print(f"❌ 錯誤：找不到檔案 {excel_file}")
        return

    # 1. 讀取 Excel 所有分頁
    try:
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        print(f"📄 偵測到 Excel 包含以下工作表: {sheet_names}")
    except Exception as e:
        print(f"❌ 無法讀取 Excel 檔案: {e}")
        return

    with app.app_context():
        # 為了避免外鍵衝突 (Foreign Key Error)，我們必須先清空「子表」，再清空「主表」
        # 匯入時則相反：先匯入「主表」，再匯入「子表」
        
        print("\n🧹 步驟 1: 清空現有資料庫 (為了確保資料乾淨)...")
        try:
            # 關閉外鍵檢查以方便清空 (SQLite 特定指令)
            db.session.execute(text("PRAGMA foreign_keys=OFF;"))
            
            # 清空所有表 (這裡列出你專案中所有的表)
            num_attempts = db.session.query(QuizAttempt).delete()
            num_questions = db.session.query(Question).delete()
            # db.session.query(User).delete() # 如果有的話
            
            db.session.commit()
            print(f"   已清空舊資料: {num_questions} 題題目, {num_attempts} 筆測驗記錄。")
            
            # 開啟外鍵檢查
            db.session.execute(text("PRAGMA foreign_keys=ON;"))
        except Exception as e:
            print(f"⚠️ 清空資料時發生警告 (通常可忽略): {e}")
            db.session.rollback()

        print("\n📥 步驟 2: 開始匯入資料...")

        # --- 匯入順序 1: Question (主表) ---
        # 這裡假設 Excel 的分頁名稱叫做 'questions' 或 'Sheet1'，請根據實際情況調整
        # 你的備份檔通常會用 table name 當作 sheet name
        
        if 'questions' in sheet_names:
            target_sheet = 'questions'
        elif 'Sheet1' in sheet_names: 
            # 假設第一頁是題目
            target_sheet = 'Sheet1'
        else:
            target_sheet = None

        if target_sheet:
            print(f"   正在匯入題目資料 (來自 {target_sheet})...")
            df_q = pd.read_excel(xls, target_sheet)
            
            # 將 DataFrame 寫入資料庫
            # 使用 pandas 的 to_sql 是最快的方法，但需要欄位名稱完全對應
            # if_exists='append' 表示加入數據，不刪除表結構
            try:
                df_q.to_sql('questions', db.engine, if_exists='append', index=False)
                print(f"   ✅ 成功匯入 {len(df_q)} 筆題目！")
            except Exception as e:
                print(f"   ❌ 匯入題目失敗: {e}")
        else:
            print("   ⚠️ 警告：找不到 'questions' 分頁，跳過題目匯入。")


        # --- 匯入順序 2: QuizAttempt (測驗記錄) ---
        if 'quiz_attempts' in sheet_names:
            print(f"   正在匯入測驗記錄 (來自 quiz_attempts)...")
            df_a = pd.read_excel(xls, 'quiz_attempts')
            
            try:
                # 處理 datetime 欄位轉換 (以防萬一)
                if 'timestamp' in df_a.columns:
                    df_a['timestamp'] = pd.to_datetime(df_a['timestamp'])
                
                df_a.to_sql('quiz_attempts', db.engine, if_exists='append', index=False)
                print(f"   ✅ 成功匯入 {len(df_a)} 筆測驗記錄！")
            except Exception as e:
                print(f"   ❌ 匯入測驗記錄失敗: {e}")
        else:
            print("   ℹ️ 提示：Excel 中沒有 'quiz_attempts' 分頁 (如果是新系統可能還沒有記錄)。")

        # --- 匯入其他表 (如果有) ---
        # 這裡可以依樣畫葫蘆加入其他 table

        print("\n🏁 還原工作完成！")
        final_q_count = Question.query.count()
        final_a_count = QuizAttempt.query.count()
        print(f"📊 目前資料庫狀態: 題目 {final_q_count} 筆 / 測驗記錄 {final_a_count} 筆")
        
        # 檢查檔案大小
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"💾 資料庫檔案大小: {size_mb:.2f} MB")

if __name__ == "__main__":
    restore_all_tables()