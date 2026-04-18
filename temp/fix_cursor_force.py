
import os
import re
import base64

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在修復游標 (強制 JS 覆寫模式)...")

# 1. 準備實心橡皮擦的 Base64 圖片
svg_content = """<svg width="24" height="24" viewBox="0 0 24 24" fill="%23444444" xmlns="http://www.w3.org/2000/svg"><path d="M15.14,3c-0.51,0-1.02,0.2-1.41,0.59L2.59,14.73C1.8,15.51,1.8,16.77,2.59,17.56l5.85,5.85c0.39,0.39,0.9,0.59,1.41,0.59 s1.02-0.2,1.41-0.59l11.14-11.14c0.78-0.78,0.78-2.05,0-2.83l-5.85-5.85C16.17,3.2,15.65,3,15.14,3z M14.44,5.11l4.45,4.45 l-2.13,2.13l-4.45-4.45L14.44,5.11z"/></svg>"""
b64_cursor = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
cursor_css_value = f"url('data:image/svg+xml;base64,{b64_cursor}') 2 22, auto"

# 2. 定義要注入的 JS 邏輯
# 修正變數名稱: tool -> toolName，增加 canvas 變數宣告 (如果 global scope 沒有或者為了安全)
# 這裡我們使用 id 為 'handwriting-canvas' 的 canvas
js_injection = f"""
            // [Auto-Fix] 強制切換游標樣式
            const canvas = document.getElementById('handwriting-canvas') || document.querySelector('canvas'); 
            if (canvas) {{
                if (toolName === 'eraser') {{
                    canvas.style.cursor = "{cursor_css_value}";
                }} else {{
                    canvas.style.cursor = "crosshair"; // 畫筆模式維持十字或預設
                }}
            }}
"""

# 3. 尋找 setTool 函數並注入
# 尋找 function setTool(toolName, color)  {
pattern_func = r'(function\s+setTool\s*\([^)]*\)\s*\{)'

if "canvas.style.cursor" in content and "[Auto-Fix]" in content: # 避免重複注入
     print("[Info] 檢測到 setTool 內可能已經有 Auto-Fix 游標設定，跳過注入。")
     # 這裡也可以選擇強制更新，但為求穩健先跳過
     # 若要強制更新，可用 sub 取代特定區塊
elif "canvas.style.cursor" in content:
    # 這裡我們將新的邏輯插入在 setTool 開頭
    content, count = re.subn(pattern_func, r'\1' + js_injection, content)
    if count > 0:
        print(f"[OK] 已將游標切換邏輯注入 setTool 函式 ({count} 處)。")
    else:
        print("[Error] 錯誤：找不到 setTool 函式。")
else:
    # 正常注入
    content, count = re.subn(pattern_func, r'\1' + js_injection, content)
    if count == 0:
        print("[Error] 錯誤：找不到 setTool 函式，無法注入 JS。")
    else:
        print(f"[OK] 已將游標切換邏輯注入 setTool 函式。")

# 4. 清理舊的 CSS (可選，避免混淆)
# 移除 .eraser-mode canvas { ... } 避免 CSS 優先權打架
content = re.sub(r'\.eraser-mode\s+canvas\s*\{[^}]+\}', '', content)

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[Success] 修正完成！現在切換橡皮擦時，游標會由 JavaScript 強制變更為實心圖示。")
