import pandas as pd
import re
import os
from app import app, db, Skill, SkillDependency # 匯入 app 和所有模型

def slugify(text):
    """ 簡單將中文轉為英文 ID (用於 Skill.name) """
    if not isinstance(text, str):
        return 'skill' # 如果是空值 (NaN)
    text = text.lower().replace(' ', '_').replace('(', '').replace(')', '')
    # 移除所有非英文、數字、底線的字元
    text = re.sub(r'\W+', '', text.replace('_', 'TEMP_UNDERSCORE')).replace('TEMP_UNDERSCORE', '_')
    return text or 'skill'

def import_curriculum():
    """ 
    主匯入函式：
    1. 讀取「課綱.xlsx」 (包含 generator_key)
    2. 重建資料庫 (drop_all, create_all)
    3. 匯入所有小單元
    """
    print("開始匯入新課綱資料 (使用 Pandas)...")
    
    # --- 檔案路徑設定 ---
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        excel_folder = '知識點鏈結' # 您的子資料夾名稱
        
        # --- ★★★ 修改點 ★★★ ---
        excel_file = '課綱.xlsx' # <--- 直接讀取您的 Excel 檔案
        sheet_name = '工作表1'   # <--- 指定 Excel 中的工作表名稱
        # --- ★★★ 修改點 ★★★ ---

        excel_filename = os.path.join(basedir, excel_folder, excel_file)
        
    except Exception as e:
        print(f"定義路徑時出錯: {e}")
        return 

    print(f"正在嘗試讀取 Excel: {excel_filename} (工作表: {sheet_name})")

    # === 步驟 1: 使用 Pandas 讀取 Excel ===
    try:
        # --- ★★★ 修改點 ★★★ ---
        df = pd.read_excel(excel_filename, sheet_name=sheet_name) 
        # --- ★★★ 修改點 ★★★ ---

        # 關鍵步驟：填補 Excel 合併儲存格造成的空值
        df['年級'].ffill(inplace=True)
        df['大單元'].ffill(inplace=True)
        
        # 移除「小單元」欄位為空的無效資料
        df.dropna(subset=['小單元'], inplace=True)
            
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{excel_filename}'")
        print(f"請確認 '{excel_folder}' 資料夾中存在 '{excel_file}' 檔案。")
        return 
    except Exception as e:
        if "No sheet named" in str(e):
             print(f"錯誤：在 Excel 檔案中找不到名為 '{sheet_name}' 的工作表。")
             print("請打開您的 Excel 檔，確認工作表名稱是否完全一致。")
        else:
            print(f"讀取 Excel 時發生錯誤: {e}")
        return 

    print(f"從 Excel 中讀取到 {len(df)} 筆「小單元」資料。")

    # === 步驟 2: 清空並重建資料庫 ===
    print("正在清空並重建資料庫表格...")
    try:
        with app.app_context(): # ★ 確保在 app context 中執行
            db.drop_all() # 刪除所有舊表格
            db.create_all() # 根據 app.py (含 generator_key) 建立新表格
        print("資料庫表格已成功重建。")
    except Exception as e:
        print(f"重建資料庫時發生錯誤: {e}")
        return 

    # === 步驟 3: 將所有「小單元」作為 Skill 存入資料庫 ===
    print("正在匯入所有「小單元」...")
    
    # 檢查 'generator_key' 欄位是否存在
    has_generator_key_column = 'generator_key' in df.columns
    if not has_generator_key_column:
        print("警告：您的 Excel 中找不到 'generator_key' 欄位。AI 題目生成將無法對應。")
    
    skills_to_add = [] # 先收集起來再一次加入
    for index, row in df.iterrows():
        try:
            # 取得 generator_key (如果欄位存在且有值)
            key_to_add = None
            if has_generator_key_column and pd.notna(row['generator_key']):
                # 清除 key 前後的空白
                key_to_add = str(row['generator_key']).strip() 
                if key_to_add == "": # 如果清完空白變空字串，也當作 None
                    key_to_add = None

            new_skill = Skill(
                display_name = str(row['小單元']).strip(),
                name = slugify(str(row['小單元']).strip()), # 自動產生唯一的英文 name
                description = str(row['內容']).strip() if pd.notna(row['內容']) else "...",
                grade_level = str(row['年級']).strip(),
                main_unit = str(row['大單元']).strip(),
                generator_key = key_to_add  # <--- 在這裡新增 key
            )
            skills_to_add.append(new_skill)
        except Exception as e:
            print(f"處理行 {index} ( {row.get('小單元', 'N/A')} ) 時出錯: {e}")

    # 一次性加入並提交
    if skills_to_add:
        try:
            with app.app_context(): # ★ 確保在 app context 中執行
                db.session.add_all(skills_to_add)
                db.session.commit()
            print(f"=== 成功！ {len(skills_to_add)} 筆「小單元」已全部匯入 Skill 資料表 ===")
        except Exception as e:
            with app.app_context(): # ★ 確保在 app context 中執行
                db.session.rollback()
            print(f"存入 Skill 時發生錯誤: {e}")
            return 

# --- 主程式 ---
if __name__ == "__main__":
    import_curriculum() # 呼叫上面的主函式

