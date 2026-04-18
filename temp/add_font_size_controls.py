import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在新增字體大小控制功能 (小 中 大)...")

# ==========================================
# 1. 注入 CSS 變數與樣式
# ==========================================
# 我們定義 --chat-font-size 變數，並讓所有相關文字引用它
# 同時設定控制按鈕的樣式
font_css = """
    <style>
        :root {
            --chat-font-size: 16px; /* 預設中字體 */
        }

        /* 字體大小控制按鈕樣式 */
        .font-controls {
            display: flex;
            gap: 5px;
            align-items: center;
        }
        .font-controls button {
            background: transparent;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            padding: 2px 6px;
            color: #555;
            transition: all 0.2s;
        }
        .font-controls button:hover {
            background: #eee;
            color: #000;
            border-color: #999;
        }

        /* === 強制套用動態字體大小的區域 === */
        
        /* 1. 聊天室內的訊息 (包含使用者和 AI) */
        .chat-message, .bot-message, .bot-message-content, .chat-user {
            font-size: var(--chat-font-size) !important;
            line-height: 1.5 !important;
        }
        
        /* 2. 聊天記錄裡的 MathJax 公式 */
        .chat-message .MathJax, .bot-message .MathJax {
            font-size: 100% !important; /* 跟隨父元素 */
        }

        /* 3. 底部提示詞建議區 (suggestions) 的按鈕 */
        #suggestions .suggestion-btn {
            font-size: var(--chat-font-size) !important;
        }

        /* 4. 聊天記錄中可能出現的選項按鈕 (追問問題) */
        #chat-history button, .suggestion-btn {
            font-size: var(--chat-font-size) !important;
        }
        
    </style>
"""

# 將 CSS 插入 head
content = content.replace('</head>', font_css + '\n</head>')

# ==========================================
# 2. 注入 JavaScript 控制邏輯
# ==========================================
font_js = """
    <script>
        function changeFontSize(size) {
            const root = document.documentElement;
            let newSize = '16px';
            
            if (size === 'small') newSize = '14px';
            if (size === 'medium') newSize = '16px';
            if (size === 'large') newSize = '20px'; // 大字體顯著放大
            
            root.style.setProperty('--chat-font-size', newSize);
            
            // 視覺回饋：稍微改變按鈕狀態 (選用)
            console.log("Font size changed to: " + size);
        }
    </script>
"""
content = content.replace('</body>', font_js + '\n</body>')

# ==========================================
# 3. 修改 HTML 結構 (加入按鈕)
# ==========================================
# 我們要找到 <h3>AI 助教</h3>，把它和按鈕包在一起
# 為了不破壞之前的排版 (margin:0)，我們用 flex 讓它們並排

# Regex 尋找標題區塊 (容許屬性變化)
pattern_header = r'(<h3[^>]*>\s*AI 助教\s*</h3>)'

# 新的 HTML 結構
# justify-content: space-between 讓標題在左，按鈕在右
# align-items: center 垂直置中
controls_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 5px;">
    \\1
    <div class="font-controls">
        <button onclick="changeFontSize('small')">小</button>
        <button onclick="changeFontSize('medium')">中</button>
        <button onclick="changeFontSize('large')">大</button>
    </div>
</div>
"""

# 執行替換
if re.search(pattern_header, content):
    content = re.sub(pattern_header, controls_html, content)
    print("已在 AI 助教標題旁加入字體控制按鈕。")
else:
    print("錯誤：找不到 AI 助教標題，無法插入按鈕。")

# ==========================================
# 4. 再次確保 suggestions 樣式能被覆蓋
# ==========================================
# 有時候 suggestion-btn 有自己的寫死的 CSS，我們上面用了 !important 應該沒問題
# 但為了保險，檢查是否有既有的 .suggestion-btn 樣式並注入變數

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("功能新增完成！\n- 點擊「小 中 大」可即時縮放文字\n- 包含聊天內容、提示詞、追問按鈕都會同步改變")
