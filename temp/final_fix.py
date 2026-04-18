
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

# --- 修正 1: 更換為「實心橡皮擦」圖示 (辨識度極高) ---
# 這個 SVG 是一個實心的塊狀物，分為兩截（手握處與擦拭處），非常直觀
solid_eraser_svg = """
            <button class="tool-btn" onclick="setTool('eraser')" title="橡皮擦" style="color: #444;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z"/>
                </svg>
            </button>"""

# 尋找原本的橡皮擦按鈕 (包含 onclick="setTool('eraser')")
btn_pattern = r'(\s*)?<button[^>]*onclick="setTool\(\'eraser\'\)"[^>]*>.*?<\/button>'
content, count_icon = re.subn(btn_pattern, solid_eraser_svg.strip(), content, flags=re.DOTALL)


# --- 修正 2: 強制對話框滿版 (使用 !important) ---
# 我們直接搜尋 .chat-message 的定義，並強制插入 width: 100% !important
# 這樣可以無視任何繼承或優先權問題

# 尋找 .chat-message { ... } 區塊
chat_css_pattern = r'(\.chat-message\s*\{[^}]*?)\}'
# 在結尾括號前，插入強制寬度設定
chat_css_fix = r'\1    width: 100% !important;\n    max-width: 100% !important;\n}'

content, count_css = re.subn(chat_css_pattern, chat_css_fix, content, flags=re.DOTALL)

# 如果 Regex 沒抓到 CSS (可能寫法不同)，直接在 </style> 前面補一個最強的樣式
if count_css == 0:
    force_style = "\n.chat-message { width: 100% !important; max-width: 100% !important; }\n"
    content = content.replace("</style>", force_style + "</style>")
    print("使用追加樣式法強制修正寬度。")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Use [OK] instead of check mark emoji to avoid cp950 encoding error
print(f"[OK] 完成！\n1. 橡皮擦圖示已換成「實心塊狀」風格。\n2. 對話框已加上 !important 強制滿版。")
