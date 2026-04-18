import pandas as pd
import os
from app import app, db, Skill, SkillDependency, SKILL_ENGINE

def import_skills_from_curriculum():
    print("開始從課綱.xlsx匯入技能結構...")

    # --- File Path Configuration ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    excel_folder = '知識點鏈結'
    excel_file = '課綱.xlsx'
    excel_filename = os.path.join(basedir, excel_folder, excel_file)
    sheet_name = '工作表1' # Assuming sheet name

    print(f"正在讀取 Excel: {excel_filename}")

    try:
        df = pd.read_excel(excel_filename, sheet_name=sheet_name)

        # --- Column Names ---
        grade_col = '年級'
        main_unit_col = '大單元'
        small_unit_col = '小單元'
        content_col = '內容' # New column for description
        generator_key_col = 'generator_key'

        # Check if columns exist
        required_cols = [grade_col, main_unit_col, small_unit_col, content_col, generator_key_col]
        if not all(col in df.columns for col in required_cols):
            print(f"錯誤：Excel 中找不到必要的欄位。請確保檔案中包含 {required_cols} 這幾欄。")
            return

        # --- Clear old data ---
        print("正在清空舊的 Skills 和 Dependencies...")
        db.session.query(SkillDependency).delete()
        db.session.query(Skill).delete()
        db.session.commit()
        print("舊資料已清空。")

        # --- Iterate through Excel and create skills ---
        for index, row in df.iterrows():
            skill_id_from_excel = row[generator_key_col]
            display_name = row[small_unit_col]
            description_from_excel = row[content_col] # Get description from '內容' column

            # Skip rows where there is no generator_key or no display name (small_unit_col)
            if pd.isna(skill_id_from_excel) or pd.isna(display_name):
                continue

            # Check if the key from Excel exists in our engine
            if skill_id_from_excel not in SKILL_ENGINE:
                print(f"  [警告] Excel中的key '{skill_id_from_excel}' 在 SKILL_ENGINE 中找不到，將跳過 '{display_name}'。")
                continue

            # Create the new skill
            new_skill = Skill(
                name=skill_id_from_excel,
                display_name=display_name,
                grade_level=row[grade_col],
                main_unit=row[main_unit_col],
                # Use description from Excel if available, otherwise use placeholder from SKILL_ENGINE
                description=description_from_excel if pd.notna(description_from_excel) else SKILL_ENGINE[skill_id_from_excel].get('description', '')
            )
            db.session.add(new_skill)
            print(f"  [建立 Skill]: {display_name} (ID: {skill_id_from_excel})")

        db.session.commit()
        print("=== 所有技能已成功從課綱匯入資料庫 ===")

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{excel_filename}'")
        return
    except Exception as e:
        print(f"處理 Excel 檔案時發生錯誤: {e}")
        db.session.rollback()
        return

# --- Main execution block ---
if __name__ == "__main__":
    with app.app_context():
        import_skills_from_curriculum()