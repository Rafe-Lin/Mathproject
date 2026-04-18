
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] 錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"[Info] 正在優化 UI (檔案大小: {len(content)} bytes)...")

# ==========================================
# 1. 準備素材
# ==========================================

# (A) 實心橡皮擦圖示 (按鈕用)
solid_eraser_icon = """<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z"/>
                </svg>"""

# (B) 實心橡皮擦游標 (CSS cursor 用，已轉為 Data URI)
# 筆尖座標設為 2 22 (左下角)
cursor_uri = "data:image/svg+xml;utf8,<svg width='24' height='24' viewBox='0 0 24 24' fill='%23444444' xmlns='http://www.w3.org/2000/svg'><path d='M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z'/></svg>"

# (C) 強制滿版 CSS 補丁
css_patch = """
        /* === [UI 優化補丁] === */
        /* 1. 容器滿版 */
        #question-container, #scratchpad-container {
            max-width: 100% !important;
            width: 100% !important;
        }
        /* 2. 對話氣泡滿版 */
        .chat-message, .chat-ai, .chat-user {
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
"""

# ==========================================
# 2. 執行替換
# ==========================================

# (1) 替換按鈕圖示
# 尋找 onclick="setTool('eraser')" 按鈕內的 <svg>
pattern_btn = r'(<button[^>]*onclick="setTool\(\'eraser\'\)"[^>]*>\s*)<svg.*?>.*?<\/svg>(\s*<\/button>)'
content, c1 = re.subn(pattern_btn, r'\1' + solid_eraser_icon + r'\2', content, flags=re.DOTALL)

# (2) 替換游標樣式
# 智能判斷：優先尋找 JS 中的 const eraserCursor，其次尋找 CSS 中的 .eraser-mode 或 .eraser-cursor
c2 = 0

# 嘗試 A: 匹配 JS 變數 (目前最可能的實作)
# 匹配 const eraserCursor = "url('...');" 結構
pattern_js_cursor = r'(const\s+eraserCursor\s*=\s*[\'"]url\([\'"])(?:.*?)([\'"]\)\s*)(?:\d+\s+\d+|auto)(.*?;)'
def replace_js_cursor(match):
    return match.group(1) + cursor_uri + match.group(2) + "2 22" + match.group(3)

content, count_js = re.subn(pattern_js_cursor, replace_js_cursor, content, flags=re.DOTALL)
c2 += count_js

# 嘗試 B: 匹配 CSS 定義 (回退方案)
pattern_css_cursor = r'(\.eraser-mode\s+canvas\s*\{\s*cursor:\s*url\()[^\)]+(\)\s*)\d+\s+\d+(,\s*auto)'
if c2 == 0: # 只有在 JS 沒找到時才試 CSS，避免重複計算(雖然這裡不衝突)
    content, count_css = re.subn(pattern_css_cursor, r'\1' + cursor_uri + r'\2' + "2 22" + r'\3', content)
    c2 += count_css

# (3) 注入 CSS 補丁
# 避免重複注入
if "/* === [UI 優化補丁] === */" not in content:
    # 檢查是否已經有類似的補丁 (例如上一步的 upgrade patch)，如果有，我們就視為已存在或追加
    if "/* === [自動套用] 樣式升級補丁 === */" in content:
         # 已經有升級補丁，就不重複加了，除非我們想覆蓋。
         # 這裡假設之前的補丁已經包含了必要的規則。
         c3 = 0
         print("[Info] 偵測到已存在樣式補丁，跳過追加。")
    elif "</style>" in content:
        content = content.replace("</style>", css_patch + "\n    </style>")
        c3 = 1
    else:
        c3 = 0
else:
    c3 = 0  # 已存在

# ==========================================
# 3. 存檔
# ==========================================
if "</html>" in content[-500:]: # 簡單檢查檔案完整性
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] UI 優化完成！\n- 按鈕圖示更新: {c1}\n- 游標樣式更新: {c2}\n- CSS 補丁注入: {c3}")
else:
    print("[Error] 檔案結尾似乎不完整，取消寫入以策安全。")
