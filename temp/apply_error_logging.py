# -*- coding: utf-8 -*-
# 此腳本用於修改 core/ai_analyzer.py 和 core/routes.py
# 實作錯誤記錄功能

import re
import sys

# 設定輸出編碼
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# ===== 步驟 1: 修改 core/ai_analyzer.py =====
print("步驟 1: 修改 core/ai_analyzer.py...")

with open(r'c:\Mathproject\core\ai_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到並替換 JSON 格式部分
old_pattern = r'"next_question":\s*true\s+或\s+false\s*\}'

new_json_fields = ''',
  "error_type": "如果答錯,請從以下選擇一個:'計算錯誤'、'觀念錯誤'、'粗心'、'其他'。如果答對則為 null",
  "error_description": "如果答錯,簡短描述錯誤原因(例如:正負號弄反、公式背錯),30字以內。如果答對則為 null",
  "improvement_suggestion": "如果答錯,給學生的具體改進建議,30字以內。如果答對則為 null"
}'''

# 替換
if re.search(old_pattern, content):
    content = re.sub(old_pattern, '"next_question": true 或 false' + new_json_fields, content)
    with open(r'c:\Mathproject\core\ai_analyzer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] ai_analyzer.py 修改完成")
else:
    print("[FAIL] 找不到要替換的 JSON 格式")

# ===== 步驟 2 & 3: 修改 core/routes.py =====
print("\n步驟 2 & 3: 修改 core/routes.py...")

with open(r'c:\Mathproject\core\routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 analyze_handwriting 函數的位置
modified = False
for i, line in enumerate(lines):
    # 步驟 2: 加上 @login_required
    if '@practice_bp.route(\'/analyze_handwriting\'' in line:
        if i+1 < len(lines) and '@login_required' not in lines[i+1]:
            lines.insert(i+1, '@login_required\n')
            print("[OK] 加上 @login_required 裝飾器")
            modified = True
            break

# 重新讀取以處理步驟 3
if modified:
    with open(r'c:\Mathproject\core\routes.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    with open(r'c:\Mathproject\core\routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

# 步驟 3: 加入錯誤記錄邏輯
for i, line in enumerate(lines):
    if 'update_progress(current_user.id, state[\'skill\'], False)' in line:
        # 找到這行後,檢查下一行是否已經有錯誤記錄邏輯
        if i+2 < len(lines) and '記錄錯誤到資料庫' not in lines[i+2]:
            indent = '        '
            error_logging_code = f'''
{indent}# 記錄錯誤到資料庫
{indent}try:
{indent}    from models import MistakeLog
{indent}    
{indent}    mistake_log = MistakeLog(
{indent}        user_id=current_user.id,
{indent}        skill_id=state['skill'],
{indent}        question_content=state['question'],
{indent}        user_answer="手寫作答(圖片)",
{indent}        correct_answer=state.get('correct_answer', '未知'),
{indent}        error_type=result.get('error_type'),
{indent}        error_description=result.get('error_description'),
{indent}        improvement_suggestion=result.get('improvement_suggestion')
{indent}    )
{indent}    db.session.add(mistake_log)
{indent}    db.session.commit()
{indent}except Exception as e:
{indent}    current_app.logger.error(f"記錄錯誤失敗: {{e}}")
{indent}    db.session.rollback()
{indent}    # 不影響主流程,繼續執行
'''
            lines.insert(i+1, error_logging_code)
            print("[OK] 加入錯誤記錄邏輯")
            break

with open(r'c:\Mathproject\core\routes.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n[SUCCESS] 所有修改完成!")
print("\n請檢查修改後的檔案:")
print("- c:\\Mathproject\\core\\ai_analyzer.py")
print("- c:\\Mathproject\\core\\routes.py")
