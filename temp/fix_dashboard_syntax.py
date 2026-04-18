# 修正 dashboard.html 中的 Jinja2 語法錯誤
dashboard_path = r'c:\Mathproject\templates\dashboard.html'

print("Reading dashboard.html...")
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除錯誤的反斜線跳脫符號
# 將 url_for(\'core.student_diagnosis\') 改為 url_for('core.student_diagnosis')
old_text = "{{ url_for(\\'core.student_diagnosis\\') }}"
new_text = "{{ url_for('core.student_diagnosis') }}"

if old_text in content:
    content = content.replace(old_text, new_text)
    print("Found and fixed the error!")
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: dashboard.html fixed!")
else:
    print("ERROR: Could not find the problematic text")
    print("Searching for variations...")
    # 檢查是否有其他變體
    if "student_diagnosis" in content:
        print("Found student_diagnosis in file")
        # 找到包含此文字的行
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "student_diagnosis" in line:
                print(f"Line {i}: {line.strip()}")
