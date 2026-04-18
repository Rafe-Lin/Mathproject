import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在微調 AI 助教區域排版 (緊湊 + 粗體)...")

# ==========================================
# 1. 處理「你好，有問題問我~」
# ==========================================
# 目標：找到包住這句話的標籤 (可能是 <p>, <div> 或 <span>)，強制加入 style
# Regex 邏輯：尋找 <tag ...>你好，有問題問我~</tag>
# 我們直接用這句話的周圍來替換，確保最精準

target_text = "你好，有問題問我~"

# 我們將整段標籤替換掉，改用我們自己定義的乾淨 div
# 為了避免誤刪其他屬性，我們先嘗試尋找簡單的包裹
# 如果找不到標籤包裹（純文字），就直接包一層 div

# 樣式：粗體、無 margin、字體微調、灰色改深一點點(若需要)
new_html = f'<div style="font-weight: bold; margin: 0; padding: 2px 0 10px 0; color: #333;">{target_text}</div>'

# 嘗試尋找 <p>你好...</p> 或 <div>你好...</div>
pattern_text_container = r'<[a-zA-Z0-9]+[^>]*>\s*' + re.escape(target_text) + r'\s*</[a-zA-Z0-9]+>'

if re.search(pattern_text_container, content):
    content = re.sub(pattern_text_container, new_html, content)
    print("已將歡迎詞改為粗體並移除多餘間距。")
else:
    # 如果找不到包裹標籤 (可能只是純文字混在裡面)，直接替換文字本身
    # 這樣會把它包起來，確保樣式生效
    if target_text in content:
        content = content.replace(target_text, new_html)
        print("已為歡迎詞文字加上粗體樣式容器。")
    else:
        print("警告：找不到「你好，有問題問我~」這段文字，可能已被修改。")

# ==========================================
# 2. 處理「AI 助教」標題間距
# ==========================================
# 我們希望標題和下面的歡迎詞靠得近一點
# 尋找 <h3>AI 助教</h3> 或 <h2>...
# 強制把它的 margin-bottom 設為 0

pattern_header = r'(<(h[1-6]|div)[^>]*>)\s*(AI 助教)\s*(</\2>)'

def reduce_header_margin(match):
    tag_start = match.group(1)
    text = match.group(3) # AI 助教
    tag_end = match.group(4)
    
    # 在 tag_start 裡面加入或修改 style
    # 簡單作法：直接替換整個 tag_start 為帶有 style 的版本
    # 但為了保留 class，我們插在 > 前面
    
    style_str = ' style="margin-bottom: 0; padding-bottom: 2px;"'
    
    if "style=" in tag_start:
        # 如果原本有 style，就在裡面加
        new_start = re.sub(r'style="([^"]*)"', r'style="\1; margin-bottom: 0; padding-bottom: 2px;"', tag_start)
    else:
        # 如果沒有，插入 style
        new_start = tag_start.replace('>', style_str + '>')
        
    return f"{new_start}{text}{tag_end}"

if re.search(pattern_header, content):
    content = re.sub(pattern_header, reduce_header_margin, content)
    print("已縮小「AI 助教」標題的底部間距。")
else:
    # 嘗試找純文字的標題 (可能在 navbar 或其他 div)
    print("未檢測到標準標題標籤的「AI 助教」，可能結構較特殊，主要依賴第一步調整。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("排版微調完成！請重新整理網頁查看效果。")
