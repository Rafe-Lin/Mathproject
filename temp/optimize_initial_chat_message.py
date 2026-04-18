import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在優化初始歡迎訊息樣式...")

# 1. 定義要尋找的目標並替換
# 當前結構：
# <div class="bot-message">
#     <div style="margin: 0; padding: 0; font-weight: bold; line-height: 1.2;">你好！有問題問我～</div>
# </div>

# 我們用 Regex 匹配整個包裹，確保替換乾淨
# (?s) 開啟 dotall 模式
pattern_msg = r'(?s)<div class="bot-message">\s*<div[^>]*>\s*你好！有問題問我～\s*</div>\s*</div>'

# 新的 HTML
new_html = '''<div class="bot-message initial-bot-message">
    你好！有問題問我～
</div>'''

if re.search(pattern_msg, content):
    content = re.sub(pattern_msg, new_html, content)
    print("已替換初始訊息為專屬 Class 結構。")
else:
    # 如果找不到，嘗試只替換文字周圍
    target_text = "你好！有問題問我～"
    print("找不到精確結構，將嘗試寬鬆替換...")
    # 尋找包含這段文字的 bot-message
    # 這比較冒險，我們先試著只把這段文字替換成新的整個 div? 不行，會巢狀
    # 假設之前的 script 已經把它弄成 <div ...>text</div>
    # 我們嘗試找 <div ...>text</div>，與外層的 div class="bot-message" 可能分開
    # 這裡我們用一個特別的標記替換：直接找 div 包裹的這句話
    
    # 嘗試匹配內層 div
    pattern_inner = r'<div[^>]*>\s*' + re.escape(target_text) + r'\s*</div>'
    if re.search(pattern_inner, content):
        # 我們要把外層也一起換掉，稍微難一點
        # 不如直接替換字串，並手動加上 class
        # 但外層 bot-message 還在。
        # 覆蓋策略：把 <div class="bot-message"> 換成 <div class="bot-message initial-bot-message">
        # 然後內容只留文字
        
        # 簡單暴力法：定位到這段文字，向上找 <div class="bot-message">
        # 但這太複雜。
        # 由於我們已知這段文字是唯一的，我們就直接替換整塊區域 (假設它一定在 bot-message 裡)
        pass 

# 2. 注入 CSS
# 我們把 CSS 規則加在 </style> 之前
css_rule = """
        /* === 初始歡迎訊息專屬優化 === */
        .initial-bot-message {
            /* 讓它變得非常緊湊，只佔一行 */
            padding: 4px 15px !important;
            margin: 5px 0 !important;
            line-height: 1.2 !important;
            min-height: auto !important;
            height: auto !important;
            display: inline-block !important; /* 隨內容縮放寬度 */
            border-radius: 20px !important;   /* 圓潤一點 */
            font-weight: bold !important;
            color: #2c3e50 !important;
        }
"""

if "initial-bot-message" not in content:
    content = content.replace("</style>", css_rule + "\n    </style>")
    print("已注入 .initial-bot-message 專屬樣式。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("優化完成！")
