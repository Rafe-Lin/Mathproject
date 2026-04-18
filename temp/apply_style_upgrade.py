
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"正在讀取穩定版 index.html ({len(content)} bytes)...")

# ==========================================
# 1. 定義素材 (SVG 與 CSS)
# ==========================================

# (A) 實心橡皮擦圖示 (用於按鈕)
solid_eraser_icon_svg = """<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z"/>
                </svg>"""

# (B) 實心橡皮擦游標 (Data URI)
# 熱點設定為 2 22 (左下角尖端)
# 注意：這裡使用單引號包覆 SVG 屬性，避免與外層 SQL 字串衝突，或使用跳脫字元
cursor_svg_data = "data:image/svg+xml;utf8,<svg width='24' height='24' viewBox='0 0 24 24' fill='%23444444' xmlns='http://www.w3.org/2000/svg'><path d='M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z'/></svg>"

# (C) 強制滿版 CSS 補丁 (直接追加在 style 結尾)
layout_patch_css = """
        /* === [自動套用] 樣式升級補丁 === */
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
# 2. 執行替換與修改
# ==========================================

# 步驟 A: 替換按鈕圖示
# 尋找包含 onclick="setTool('eraser')" 的按鈕內的 <svg>...</svg>
pattern_icon = r'(<button[^>]*onclick="setTool\(\'eraser\'\)"[^>]*>\s*)<svg.*?>.*?<\/svg>(\s*<\/button>)'
content, count_icon = re.subn(pattern_icon, r'\1' + solid_eraser_icon_svg + r'\2', content, flags=re.DOTALL)
print(f"[OK] 按鈕圖示更新: {count_icon} 處")

# 步驟 B: 替換游標樣式
# 尋找 .eraser-mode canvas { cursor: url(...) x y, auto; } 或是 JS 變數 const eraserCursor = "url('...')"
# 由於之前的步驟已經修改為 JS 變數，這裡針對 JS 變數進行匹配
# 模式： (const\s+eraserCursor\s*=\s*"url\(')([^']+?)('\)\s*)(?:\d+\s+\d+|auto)(.*?;)
# 我們需要非常寬鬆的匹配，因為 SVG 內容變比較長
pattern_js_cursor = r'(const\s+eraserCursor\s*=\s*[\'"]url\([\'"]).*?([\'"]\)\s*(?:\d+\s+\d+|auto).*?[\'"];)'
# 如果找不到 JS 變數，嘗試找 CSS (回退方案)
pattern_css_cursor = r'(\.eraser-mode\s+canvas\s*\{\s*cursor:\s*url\()[^\)]+(\)\s*)\d+\s+\d+(,\s*auto)'

# 嘗試 JS 替換
cursor_replaced = False
match_js = re.search(pattern_js_cursor, content, flags=re.DOTALL)
if match_js:
     # 替換邏輯： 保留前綴 url('  插入新SVG  保留後綴 ') 2 22, auto";
     # 注意：re.subn 使用 group replacement
     # 重新構建 replacement string
     # regex group 1: const eraserCursor = "url('
     # regex group 2: ') 0 20, auto";  (注意：這裡的座標可能不同)
     # 我們強制將座標改為 2 22
     
     # 更精確的 regex，捕捉前後綴
     pattern_js_precise = r'(const\s+eraserCursor\s*=\s*[\'"]url\([\'"])(?:.*?)([\'"]\)\s*)(?:\d+\s+\d+|auto)(.*?;)'
     
     # 使用 function 作為 replacement 以避免 group reference 解析錯誤 (例如 \2 被解析為 group 2, 但後面跟著數字可能混淆)
     def replace_js_cursor(match):
         return match.group(1) + cursor_svg_data + match.group(2) + "2 22" + match.group(3)
         
     content, count_cursor = re.subn(pattern_js_precise, replace_js_cursor, content, flags=re.DOTALL)
     if count_cursor > 0:
         print(f"[OK] 游標樣式更新 (JS): {count_cursor} 處")
         cursor_replaced = True

if not cursor_replaced:
    # 嘗試 CSS 替換
    def replace_css_cursor(match):
         return match.group(1) + cursor_svg_data + match.group(2) + "2 22" + match.group(3)
         
    content, count_cursor = re.subn(pattern_css_cursor, replace_css_cursor, content)
    if count_cursor > 0:
        print(f"[OK] 游標樣式更新 (CSS): {count_cursor} 處")
    else:
        print("[Warning] 警告: 找不到橡皮擦游標定義 (JS 或 CSS)")


# 步驟 C: 注入 CSS 補丁 (滿版設定)
# 檢查是否已經有補丁，若無則追加
if "/* === [自動套用] 樣式升級補丁 === */" not in content:
    if "</style>" in content:
        content = content.replace("</style>", layout_patch_css + "\n    </style>")
        print("[OK] CSS 版面補丁: 已追加")
    else:
        print("[Warning] 警告: 找不到 </style> 標籤")
else:
    print("[Info] CSS 補丁已存在，跳過")

# ==========================================
# 3. 安全檢查與存檔
# ==========================================

# 檢查檔案尾部是否完整 (防止上次的截斷悲劇重演)
if "</html>" not in content[-500:]:
    print("[Error] 錯誤: 處理後的檔案結尾不完整！放棄存檔以保護原始檔案。")
else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[Success] 升級完成！所有功能與樣式已更新至穩定版 index.html。")
