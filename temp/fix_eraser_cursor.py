
import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在讀取 index.html 並鎖定橡皮擦游標設定...")

# 2. 定義新版「實心橡皮擦」的 SVG 資料 (用於游標)
# 我們需要將 SVG 編碼為 Data URI 格式。
# 這裡將 fill 設為深灰色 (%23444444) 以便在白色畫布上清楚可見。
new_cursor_svg_encoded = """<svg width="24" height="24" viewBox="0 0 24 24" fill="%23444444" xmlns="http://www.w3.org/2000/svg"><path d="M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z"/></svg>"""

# 3. 使用 Regex 精準尋找 CSS 中的游標定義
# 修正目標模式：我們目前在 JS 中的變數 const eraserCursor = "url('...')"
# 目標是 JS 中的 eraserCursor 變數定義，而非 CSS 類別
# pattern = r'(\.eraser-mode\s+canvas\s*\{\s*[^}]*?cursor:\s*url\(\s*[\'"]data:image/svg\+xml;utf8,)(<svg.*?>.*?<\/svg>)([\'"]\)\s*(?:\d+\s+\d+|auto).*?;\s*\})' # 這是舊的 CSS 模式，這裡不適用
# 我們需要針對 JS 中的變數定義進行替換

# 尋找 JS 變數定義： const eraserCursor = "url('data:image/svg+xml;utf8,<svg...svg>') 0 20, auto";
# 我們分為三部分：前綴 (url('...)，SVG 內容，後綴 (') 0 20, auto";)
pattern_js = r'(const\s+eraserCursor\s*=\s*[\'"]url\([\'"]data:image/svg\+xml;utf8,)(<svg.*?>.*?<\/svg>)([\'"]\)\s*(?:\d+\s+\d+|auto).*?[\'"];)'

def replace_cursor_data_js(match):
    prefix = match.group(1)
    # match.group(2) 是舊的 SVG
    suffix = match.group(3)
    
    # 更新游標熱點
    new_suffix = re.sub(r'\d+\s+\d+', '2 22', suffix)
    
    return prefix + new_cursor_svg_encoded + new_suffix

# 執行 JS 變數替換
new_content, count = re.subn(pattern_js, replace_cursor_data_js, content, flags=re.DOTALL)

if count > 0:
    # 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] 成功！已將 {count} 處 JS 中的橡皮擦游標變數替換為新版實心圖示，並調整熱點至尖端。")
else:
    # 如果 JS 沒抓到，嘗試抓 CSS (可能使用者還是想嘗試修 CSS，雖然我們之前改成 JS 了)
    # 保留原本的 CSS 替換邏輯作為備案，或者針對 CSS .eraser-cursor 類別
     pattern_css = r'(\.eraser-cursor\s*\{\s*cursor:\s*url\(\s*[\'"]data:image/svg\+xml;utf8,)(<svg.*?>.*?<\/svg>)([\'"]\)\s*(?:\d+\s+\d+|auto).*?;\s*\})'
     new_content, count_css = re.subn(pattern_css, replace_cursor_data_js, content, flags=re.DOTALL) # 重用 replace function 因為結構類似
     
     if count_css > 0:
         with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
         print(f"[OK] 成功！已將 {count_css} 處 CSS (.eraser-cursor) 的游標替換。")
     else:
         print("[Warning] 找不到符合的橡皮擦游標定義 (JS變數 或 CSS類別)。")

