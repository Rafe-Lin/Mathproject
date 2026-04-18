
import os
import re
from datetime import datetime

TEMPLATES_DIR = r'd:\Python\Mathproject\templates'
TARGET_VERSION = "V2.0"
TARGET_DATE = "2026-01-13"
MAINTAINER = "Math AI Project Team"

# Map filename to (Backend Call, Description)
TEMPLATE_MAP = {
    "_admin_navbar.html": ("Include File", "後台管理導覽列 (Include)"),
    "add_mistake.html": ("core/routes/analysis.py -> add_mistake_page", "新增錯題頁面"),
    "admin_curriculum.html": ("core/routes/admin.py -> admin_curriculum", "後台課程綱要管理"),
    "admin_examples.html": ("core/routes/admin.py -> admin_examples", "後台例題管理"),
    "admin_prerequisites.html": ("core/routes/admin.py -> admin_prerequisites", "後台前置技能管理"),
    "admin_skills.html": ("core/routes/admin.py -> admin_skills", "後台技能管理"),
    "ai_prompt_settings.html": ("core/routes/admin.py -> ai_prompt_settings_page", "AI Prompt 參數設定"),
    "dashboard.html": ("app.py -> dashboard", "學生/教師儀表板"),
    "db_maintenance.html": ("core/routes/admin.py -> db_maintenance", "資料庫維護與備份"),
    "exam_upload.html": ("core/routes/exam.py -> exam_upload_page", "考卷上傳與分析"),
    "grade_view.html": ("(Dynamic/Orphan) -> show_grade", "年級大單元檢視"),
    "image_quiz_generator.html": ("core/routes/practice.py -> image_quiz_generator", "圖片生成測驗"),
    "importer_status.html": ("core/routes/admin.py -> importer_status", "教科書匯入進度顯示"),
    "index.html": ("core/routes/practice.py -> practice", "學生練習主頁面"),
    "login.html": ("app.py -> login", "使用者登入頁面"),
    "mistake_notebook.html": ("core/routes/analysis.py -> mistake_notebook", "學生錯題本"),
    "register.html": ("app.py -> register", "使用者註冊頁面"),
    "similar_questions.html": ("core/routes/practice.py -> similar_questions_page", "相似題生成練習"),
    "student_diagnosis.html": ("core/routes/analysis.py -> student_diagnosis", "學生學習診斷"),
    "teacher_analysis.html": ("app.py -> teacher_analysis", "教師分析儀表板"),
    "teacher_dashboard.html": ("app.py -> teacher_dashboard", "教師管理儀表板"),
    "textbook_importer.html": ("core/routes/admin.py -> admin_textbook_importer", "教科書匯入介面"),
    "unit_view.html": ("(Dynamic/Orphan) -> show_unit", "小單元選擇檢視")
}

HEADER_TEMPLATE = """<!--
=============================================================================
模組名稱 (Module Name): {filename}
功能說明 (Description): {description}
後端呼叫 (Backend Call): {backend_call}
版本資訊 (Version): {version}
更新日期 (Date): {date}
維護團隊 (Maintainer): {maintainer}
=============================================================================
-->
"""

def update_html_header(filepath, filename):
    if filename not in TEMPLATE_MAP:
        print(f"Skipping {filename} (Not in map)")
        return

    backend_call, description = TEMPLATE_MAP[filename]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content = "".join(lines)
    
    # 1. Remove existing header if present (heuristic: matches Module Name pattern)
    # We'll use a regex to identify and strip the comment block if it looks like our header
    # But be careful not to strip other comments.
    
    # Simple regex for our standard header block
    header_regex = re.compile(r'<!--\s*=+\s*模組名稱 \(Module Name\):.*?=+\s*-->\s*', re.DOTALL)
    content = header_regex.sub('', content)
    
    # Re-split into lines after removal
    lines = content.splitlines(keepends=True)

    # 2. Generate New Header
    new_header = HEADER_TEMPLATE.format(
        filename=f"templates/{filename}",
        description=description,
        backend_call=backend_call,
        version=TARGET_VERSION,
        date=TARGET_DATE,
        maintainer=MAINTAINER
    )

    # 3. Determine Insertion Point
    insert_idx = 0
    
    # Check for {% extends %} in the first few lines
    for i, line in enumerate(lines[:10]):
        if line.strip().startswith('{% extends'):
            insert_idx = i + 1
            break
            
    # Insert
    if insert_idx == 0:
        # Prepend
        final_lines = [new_header] + lines
    else:
        # Insert after extends
        final_lines = lines[:insert_idx] + [new_header] + lines[insert_idx:]

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print(f"Updated {filename}")

def main():
    if not os.path.exists(TEMPLATES_DIR):
        print(f"Directory not found: {TEMPLATES_DIR}")
        return

    count = 0
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            try:
                update_html_header(filepath, filename)
                count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"Processed {count} files.")

if __name__ == "__main__":
    main()
