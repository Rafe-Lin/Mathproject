
import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在讀取 index.html...")

# 2. 定義修正後的 CSS 樣式
# 我們直接把 .chat-message 的定義整個換掉，確保萬無一失
# 將 max-width 強制設為 100% 並加上 box-sizing
new_chat_css = """
        .chat-message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
            max-width: 100%; /* 強制滿版 */
            width: 100%;     /* 確保寬度 */
            box-sizing: border-box; /* 防止 padding 撐破 */
        }
"""

# 3. 使用 Regex 尋找原本的 .chat-message 區塊
# 尋找以 .chat-message 開頭，直到遇到下一個 } 結束的區塊
pattern = r'\.chat-message\s*\{[^}]*\}'

# 4. 執行替換
new_content, count = re.subn(pattern, new_chat_css.strip(), content, flags=re.DOTALL)

if count > 0:
    # 5. 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    # Using simple text instead of emoji to avoid cp950 errors
    print(f"[OK] 成功！已強制將 .chat-message 的寬度設為 100% (修改了 {count} 處)。")
else:
    # 如果 Regex 沒抓到，嘗試直接替換關鍵字
    if "max-width: 80%" in content:
        content = content.replace("max-width: 80%", "max-width: 100%")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[OK] 成功！使用關鍵字替換將 80% 改為 100%。")
    # Added check for already 100%
    elif "max-width: 100%" in content and ".chat-message" in content:
         print("[OK] 成功！檢測到 .chat-message 已經是 100% 寬度。")
    else:
        print("⚠️ 警告：找不到 .chat-message 或 max-width: 80% 的設定，請確認檔案內容。")
