import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在執行終極排版修復 (CSS 強制覆蓋)...")

# ==========================================
# 1. 注入 CSS 強制規則 (最穩的解法)
# ==========================================
# 這段 CSS 會無視原本的標籤屬性，強制把間距壓扁
force_css = """
        /* === AI 聊天室排版強制修正 === */
        .chat-area h3 { 
            margin-bottom: 0 !important; 
            padding-bottom: 5px !important; 
            margin-top: 0 !important; 
        }
        #chat-history { 
            padding-top: 0 !important; 
            margin-top: 0 !important; 
        }
        .bot-message { 
            margin-top: 0 !important; 
            padding-top: 0 !important; 
        }
        /* 針對頑固的 pre 標籤進行降伏 */
        .bot-message pre {
            margin: 0 !important;
            padding: 0 !important;
            font-family: inherit !important; /* 消除醜醜的程式碼字體 */
            font-weight: bold !important;   /* 強制粗體 */
            white-space: pre-wrap !important; /* 保留換行但允許自動折行 */
            background-color: transparent !important;
            border: none !important;
        }
"""

if "AI 聊天室排版強制修正" in content:
    print("CSS 強制規則似乎已存在，跳過注入。")
else:
    # 尋找 CSS 結尾標籤
    if "</style>" in content:
        content = content.replace("</style>", force_css + "\n    </style>")
        print("已注入 CSS 強制規則，強制消除所有間距。")
    else:
        print("警告：找不到 </style> 標籤，無法注入 CSS。")

# ==========================================
# 2. 再次嘗試替換 HTML (補刀)
# ==========================================
# 這次我們用更寬鬆的條件，只要看到那句話，就把它的容器改成 div
target_text = "你好！有問題問我～"
new_html_tag = f'<div class="bot-message-content" style="margin:0; padding:0; font-weight:bold;">{target_text}</div>'

# 嘗試 1: <pre>你好...</pre>
pattern_pre = r'<pre[^>]*>\s*' + re.escape(target_text) + r'\s*</pre>'
content, c1 = re.subn(pattern_pre, new_html_tag, content)

# 嘗試 2: 單純找到這句話，如果它還沒被包在我們的新 div 裡
if c1 == 0 and target_text in content:
    # 檢查是否已經被改過了
    if 'class="bot-message-content"' not in content:
        # 這裡比較危險，我們只替換文字本身，希望外層 CSS 能救回來
        print("HTML 結構較複雜，將依賴 CSS 規則進行排版修正。")
    else:
        print("HTML 似乎已經是正確格式。")
else:
    print("已將 HTML 標籤替換為無格式 div。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("完成！請重新整理網頁 (Ctrl+F5) 以確保 CSS 重新載入。")
