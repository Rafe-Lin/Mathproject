import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在移除聊天區多餘留白 (Remove Spacing)...")

# ==========================================
# 1. 處理 <pre> 標籤 (元兇)
# ==========================================
# 尋找 <pre>你好！有問題問我～</pre>
# 改成 <div style="margin: 0; font-weight: bold;">你好！有問題問我～</div>

target_text = "你好！有問題問我～"
# 寬鬆匹配 <pre> 包裹的版本
pattern_pre = r'<pre[^>]*>\s*' + re.escape(target_text) + r'\s*</pre>'
# 或是我們之前可能改成 <div...>...</div> 的版本，再確保一次
pattern_div = r'<div[^>]*>\s*' + re.escape(target_text) + r'\s*</div>'

# 新的 HTML：極致緊湊，無 margin
new_html = f'<div style="margin: 0; padding: 0; font-weight: bold; line-height: 1.2;">{target_text}</div>'

if re.search(pattern_pre, content):
    content = re.sub(pattern_pre, new_html, content)
    print("已移除 <pre> 標籤，消除文字預設邊距。")
elif re.search(pattern_div, content):
    content = re.sub(pattern_div, new_html, content)
    print("已更新歡迎詞容器樣式 (更緊湊)。")
else:
    # 針對沒有標籤包裹的情況
    if target_text in content:
        content = content.replace(target_text, new_html)

# ==========================================
# 2. 處理 #chat-history 容器間距
# ==========================================
# 我們需要在 id="chat-history" 上強制加上 style="padding-top: 5px;" (原原本可能是 15px)
# 這樣標題和內容才會靠得近

# 尋找 <div id="chat-history">
# 為了避免覆蓋既有的 class 或 style，我們用小心的方式插入
pattern_id = r'(<div\s+id="chat-history"[^>]*)>'

def add_tight_padding(match):
    tag = match.group(1)
    if "style=" in tag:
        # 如果原本就有 style，插入 padding-top: 5px
        return re.sub(r'style="([^"]*)"', r'style="\1; padding-top: 5px;"', tag) + ">"
    else:
        # 如果沒有，新增 style
        return tag + ' style="padding-top: 5px;">'

content, count = re.subn(pattern_id, add_tight_padding, content)
if count > 0:
    print("已縮減 #chat-history 的上方內距。")

# ==========================================
# 3. 確保 bot-message 本身沒有怪異間距
# ==========================================
# 尋找包含歡迎詞的那一個 bot-message div
# 雖然比較難精準定位到那一個，但我們可以修改 CSS 類別定義 (如果有)
# 這裡選擇直接在 HTML 結構上微調，若前面步驟成功，應該就夠了。

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("排版修正完成！現在標題與歡迎詞應該會緊貼在一起了。")
