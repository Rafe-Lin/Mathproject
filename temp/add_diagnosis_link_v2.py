# 簡化版腳本:直接在指定行後插入新連結
dashboard_path = r'c:\Mathproject\templates\dashboard.html'

print("Reading file...")
with open(dashboard_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到包含 "考卷診斷" 的行
insert_index = None
for i, line in enumerate(lines):
    if '考卷診斷' in line and 'exam_upload_page' in line:
        # 找到下一個 </a> 的位置
        if '</a>' in line:
            insert_index = i + 1
        else:
            # 如果 </a> 在下一行
            for j in range(i+1, min(i+5, len(lines))):
                if '</a>' in lines[j]:
                    insert_index = j + 1
                    break
        break

if insert_index:
    # 插入新連結
    new_link = '            <a href="{{ url_for(\'core.student_diagnosis\') }}"\n                style="background: #8e44ad; padding: 8px 15px; border-radius: 4px;">📊 學習診斷</a>\n'
    lines.insert(insert_index, new_link)
    
    print(f"Inserting at line {insert_index}...")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("SUCCESS!")
else:
    print("ERROR: Could not find insertion point")
