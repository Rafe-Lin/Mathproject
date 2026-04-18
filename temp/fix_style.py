
import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"正在讀取 index.html ({len(content)} bytes)...")

# 2. 修改版面寬度：將原本固定的 900px 改為 68vw (約螢幕 2/3)
# 影響範圍：題目框、計算紙框、標題列、按鈕區
# 使用 Regex 替換所有 max-width: 900px
content, count_layout = re.subn(r'max-width:\s*900px', 'max-width: 68vw', content)

# 3. 修改對話框寬度：將原本的 80% 改為 100% (滿版)
# 針對 .chat-message 裡的 max-width: 80%
content, count_chat = re.subn(r'(chat-message\s*\{[^}]*?)max-width:\s*80%', r'\1max-width: 100%', content, flags=re.DOTALL)

# 補強：同時檢查 85% 的情況 (因為之前版本可能有 85%)
content, count_chat_85 = re.subn(r'(chat-message\s*\{[^}]*?)max-width:\s*85%', r'\1max-width: 100%', content, flags=re.DOTALL)
count_chat += count_chat_85

# 4. 強制補強 (如果 Regex 沒抓到，直接用字串替換確保成功)
if count_layout == 0:
    # 檢查是否已經是 68vw
    if 'max-width: 68vw' in content:
        print("版面寬度已經是 68vw，無需修改。")
    else:
        content = content.replace('max-width: 900px', 'max-width: 68vw')
        print("使用強制替換修正版面寬度 (900px -> 68vw)")

if count_chat == 0:
    # 檢查是否已經是 100%
    if 'max-width: 100%' in content and '.chat-message' in content:
        print("對話框寬度已經是 100%，無需修改。")
    else:
        content = content.replace('max-width: 80%', 'max-width: 100%')
        print("使用強制替換修正對話框寬度 (80% -> 100%)")

# 5. 確保題目框沒有被錯誤的 max-width 限制 (防止變成 100% 卻又被縮小)
# 尋找 #question-container 確保它也是 68vw (已經在步驟 2 完成)

# 6. 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 修復完成！\n- 版面寬度已調整為 68vw (修改了 {count_layout} 處)\n- 對話框已調整為 100% 滿版 (修改了 {count_chat} 處)")
