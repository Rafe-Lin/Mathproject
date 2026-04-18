# 在 dashboard.html 中新增學習診斷連結的腳本
import re

dashboard_path = r'c:\Mathproject\templates\dashboard.html'

print("Reading dashboard.html...")
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到考卷診斷連結並在其後新增學習診斷連結
old_pattern = r'(<a href="{{ url_for\(\'core\.exam_upload_page\'\) }}"\s+style="background: #e74c3c; padding: 8px 15px; border-radius: 4px;">📝 考卷診斷</a>)\s+(<a href="{{ url_for\(\'logout\'\) }}">登出</a>)'

new_content = r'\1\n            <a href="{{ url_for(\'core.student_diagnosis\') }}"\n                style="background: #8e44ad; padding: 8px 15px; border-radius: 4px;">📊 學習診斷</a>\n            \2'

# 執行替換
updated_content = re.sub(old_pattern, new_content, content)

if updated_content != content:
    print("Writing dashboard.html...")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("SUCCESS: dashboard.html updated!")
else:
    print("WARNING: No match found, may already be added")
