
import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在讀取 index.html 並進行強制修復...")

# ==========================================
# 修正 1: 強制 CSS 覆寫 (不搜尋舊代碼，直接追加新代碼)
# ==========================================
# 我們在 </style> 標籤閉合前，插入一段最強制的 CSS
# 這會覆蓋掉前面所有的 max-width: 80% 設定

override_css = """
        /* === 強制修正補丁 (由 Python 腳本插入) === */
        #question-text .chat-message {
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        /* 確保題目容器本身也是滿寬 */
        #question-container {
            max-width: 100% !important;
            width: 100% !important;
        }
"""

if "</style>" in content:
    content = content.replace("</style>", override_css + "\n    </style>")
    print("[OK] CSS 樣式已強制追加 (使用 append 策略)。")
else:
    print("[Warning] 找不到 </style> 標籤，無法追加樣式。")


# ==========================================
# 修正 2: 替換橡皮擦圖示 (針對整塊 SVG 替換)
# ==========================================
# 新的圖示 SVG (實心塊狀風格)
new_icon_svg = """<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16.24 3.56l4.95 4.94c.78.79.78 2.05 0 2.84L8.1 24.44a2.01 2.01 0 0 1-2.83 0L.29 19.5a2.008 2.008 0 0 1 0-2.83l13.11-13.11c.79-.79 2.06-.79 2.84 0zM2.83 18.08l4.56 4.56L19.46 10.5 14.9 5.94 2.83 18.08z"/>
                </svg>"""

# 使用 Regex 鎖定橡皮擦按鈕內部的 SVG
# 特徵：在 onclick="setTool('eraser')" 的按鈕裡面
pattern_icon = r'(<button[^>]*onclick="setTool\(\'eraser\'\)"[^>]*>\s*)<svg.*?>.*?<\/svg>(\s*<\/button>)'

# 執行替換
content, count = re.subn(pattern_icon, r'\1' + new_icon_svg + r'\2', content, flags=re.DOTALL)

if count > 0:
    print("[OK] 橡皮擦圖示已更換為「實心塊狀」風格。")
else:
    print("[Warning] 找不到橡皮擦圖示位置，可能程式碼結構有變。")

# ==========================================
# 寫回檔案
# ==========================================
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[Success] 所有修正已寫入 index.html")
