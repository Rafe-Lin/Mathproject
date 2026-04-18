
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] File not found: {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Removing redundant 'Clear' text button...")

# ==========================================
# 移除目標
# ==========================================
# 我們要尋找一個按鈕：
# 1. 它是 <button> 標籤
# 2. 它裡面包含 "清除" 兩個字
# 3. 它通常綁定 onclick="clearCanvas()"
# Regex 邏輯：尋找呼叫 clearCanvas 的按鈕，且內容包含 "清除"
pattern = r'<button[^>]*onclick="clearCanvas\(\)"[^>]*>\s*清除\s*<\/button>'

# 執行移除 (替換為空字串)
content, count = re.subn(pattern, '', content)

if count > 0:
    print(f"[OK] Removed {count} 'Clear' text buttons.")
    
    # 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[Success] Modification complete! Only the trash icon remains.")
else:
    print("[Warning] Could not find button with 'Clear' text.")
    print("Possible reasons:")
    print("1. Button text is not '清除'")
    print("2. Code structure mismatch")
