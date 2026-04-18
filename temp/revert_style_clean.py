
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] File not found: {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Reverting to Clean UI Style...")

# 我們保留新的 HTML 結構 (left-panel/right-panel)，但把 CSS 改回「硬派」風格
# 1. 白底黑字
# 2. 直角 (無 border-radius)
# 3. 實線邊框 (無 shadow)
# 4. 滿版利用

clean_css = """
    <style>
        /* === Clean Engineering Style === */
        :root {
            --border-color: #ccc;
            --active-color: #000;
        }

        body {
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background-color: #fff;
            color: #000;
            overflow: hidden;
        }

        /* 導航列 */
        .navbar {
            border-bottom: 1px solid #ccc;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 50px;
            background: #fff;
        }
        .navbar h1 { font-size: 1.2rem; font-weight: bold; margin: 0; }
        .user-info { font-size: 0.9rem; }
        .user-info a { color: #000; }

        /* 主版面 */
        .main-container {
            display: flex;
            flex: 1;
            height: calc(100vh - 50px);
            overflow: hidden;
        }

        /* 左側 (題目+畫布) */
        .left-panel {
            flex: 7; /* 70% 寬度 */
            display: flex;
            flex-direction: column;
            border-right: 1px solid #ccc;
            min-width: 0;
        }

        /* 右側 (對話) */
        .right-panel {
            flex: 3; /* 30% 寬度 */
            display: flex;
            flex-direction: column;
            background: #fff;
            min-width: 300px;
        }

        /* 移除卡片效果，改回純區塊 */
        .card {
            background: transparent;
            box-shadow: none;
            border-radius: 0;
            padding: 0;
            margin: 0;
        }

        /* 題目區 */
        #question-container {
            padding: 15px;
            border-bottom: 1px solid #ccc;
            font-size: 1.1rem;
            line-height: 1.5;
            background: #fff;
            /* Override potential max-height from pro UI if needed, or keep it */
            max-height: 40vh;
            overflow-y: auto;
        }

        /* 計算紙容器 */
        #scratchpad-container {
            flex: 1;
            position: relative;
            background: #fff;
            overflow: hidden;
        }

        /* 畫布 */
        #handwriting-canvas {
            width: 100%;
            height: 100%;
            display: block;
            cursor: crosshair;
        }

        /* 工具列 - 回歸簡單的頂部懸浮 */
        #scratchpad-controls {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: #fff;
            border: 1px solid #000;
            padding: 5px;
            display: flex;
            gap: 5px;
            z-index: 10;
            border-radius: 0; /* Reset radius */
        }

        /* 工具按鈕 - 簡單方塊 */
        .tool-btn {
            width: 32px;
            height: 32px;
            border: 1px solid #ddd;
            background: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 0; /* 直角 */
            padding: 0;
        }
        .tool-btn:hover { background: #eee; }
        .tool-btn.active { 
            background: #000; 
            color: #fff; 
            border-color: #000;
        }
        /* 讓 SVG 圖示在 active 狀態下變白 */
        .tool-btn.active svg { fill: #fff; }
        .tool-btn.active svg path { stroke: #fff; }

        /* 對話歷史區 */
        #chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        /* 對話氣泡 - 簡單框線 */
        .chat-message, .bot-message, .user-message {
            max-width: 90%;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.95rem;
            line-height: 1.4;
            word-wrap: break-word;
            margin-bottom: 0;
        }
        
        .bot-message {
            background: #f9f9f9;
            border: 1px solid #ddd;
            color: #000;
            align-self: flex-start;
        }

        .user-message {
            background: #e6f3ff;
            border: 1px solid #b3d7ff;
            color: #000;
            align-self: flex-end;
        }

        /* 輸入區 */
        .chat-input-area {
            padding: 10px;
            border-top: 1px solid #ccc;
            display: flex;
            flex-direction: column;
            gap: 10px;
            background: #fff;
        }
        
        .chat-input-group {
            display: flex;
            gap: 10px;
        }

        #chat-input {
            flex: 1;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 2px;
            outline: none;
            font-size: 1rem;
        }
        #chat-input:focus { border-color: #000; }

        #chat-send-button {
            width: 60px;
            background: #000; /* 純黑按鈕 */
            color: #fff;
            border: none;
            border-radius: 2px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #chat-send-button svg { fill: #fff; width: 18px; height: 18px; }

        /* Helpers */
        .symbol-buttons { display: flex; gap: 5px; flex-wrap: wrap; }
        .symbol-button { border: 1px solid #ccc; background: #fff; border-radius: 2px; cursor: pointer; }
    </style>
"""

# 使用 Regex 取代 <style>...</style>
# We need to replace only the *first* style block or the one we just injected
if "<style>" in content:
    content = re.sub(r'<style>.*?</style>', clean_css.strip(), content, count=1, flags=re.DOTALL)
    print("[OK] Replaced CSS with Clean Style.")
else:
    content = content.replace('</head>', clean_css + '\n</head>')
    print("[OK] Inserted Clean CSS.")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[Success] Reverted to Clean UI Style.")
