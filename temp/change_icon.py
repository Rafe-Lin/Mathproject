import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"正在讀取 index.html...")

# 2. 定義新的橡皮擦按鈕 HTML (包含新圖示 SVG)
# 圖示說明：這是一個經典的傾斜塊狀橡皮擦，中間有一條線代表握把套，非常直觀。
new_eraser_html = """
                                    <button class="tool-btn" onclick="setTool('eraser')" title="橡皮擦" style="color: #666;">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M20 6L9 17l-5-5 11-11a2.828 2.828 0 1 1 4 4L19 6z"></path>
                                            <path d="M12 13l5 5"></path>
                                        </svg>
                                    </button>"""

# 3. 使用 Regex 尋找舊的橡皮擦按鈕
# 特徵：尋找含有 onclick="setTool('eraser')" 的 button 標籤及其內容
# 使用 re.DOTALL 確保可以跨行匹配
pattern = r'(\s*)?<button[^>]*onclick="setTool\(\'eraser\'\)"[^>]*>.*?<\/button>'

# 4. 執行替換
new_content, count = re.subn(pattern, new_eraser_html.strip(), content, flags=re.DOTALL)

if count > 0:
    # 5. 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ 成功！已將 {count} 個橡皮擦圖示更換為「清晰傾斜版」。")
else:
    print("❌ 找不到橡皮擦按鈕，請確認 index.html 中的 onclick=\"setTool('eraser')\" 是否存在。")
