# -*- coding: utf-8 -*-
"""修改 db_maintenance 函數,添加表格過濾"""
import sys
import io

# 設定輸出編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 讀取檔案
with open('core/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到並替換目標程式碼
old_code = """        # GET request
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        return render_template('db_maintenance.html', tables=tables)"""

new_code = """        # GET request
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        # 只顯示這三個技能相關的表格
        allowed_tables = ['skills_info', 'skill_prerequisites', 'skill_curriculum']
        tables = [t for t in all_tables if t in allowed_tables]
        return render_template('db_maintenance.html', tables=tables)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    # 寫回檔案
    with open('core/routes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Modified db_maintenance function")
else:
    print("ERROR: Target code not found")
