
import os
import re

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"[Error] File not found: {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Applying Pro UI Upgrade (v2)...")

# ==========================================
# 1. New CSS Definition
# ==========================================
new_css = """
    <style>
        :root {
            --primary-color: #4f46e5;
            --primary-hover: #4338ca;
            --accent-color: #f97316;
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
            --text-main: #1f2937;
            --text-sub: #6b7280;
            --border-radius: 16px;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .navbar {
            background: var(--card-bg);
            padding: 0.75rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-sm);
            z-index: 10;
            flex-shrink: 0;
        }

        .navbar h1 {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }

        .user-info {
            font-size: 0.9rem;
            color: var(--text-sub);
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .user-info a {
            color: var(--text-sub);
            text-decoration: none;
            transition: color 0.2s;
        }
        .user-info a:hover { color: var(--primary-color); }

        .main-container {
            display: flex;
            flex: 1;
            padding: 1rem;
            gap: 1rem;
            height: calc(100vh - 60px);
            overflow: hidden;
        }

        .left-panel {
            flex: 2;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            min-width: 0;
        }

        .right-panel {
            flex: 1;
            background: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-width: 350px;
            padding: 0; /* Override default p-20 */
        }

        .card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        #question-container {
            flex: 0 0 auto;
            max-height: 40vh;
            overflow-y: auto;
            font-size: 1.2rem;
            font-weight: 600;
            line-height: 1.6;
            color: var(--text-main);
        }

        #scratchpad-container {
            flex: 1;
            padding: 0;
            overflow: hidden;
            position: relative;
        }

        /* Float Toolbar */
        #scratchpad-controls {
            position: absolute;
            top: 1rem;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            padding: 0.5rem;
            border-radius: 999px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            gap: 0.5rem;
            z-index: 20;
            border: 1px solid rgba(0,0,0,0.05);
        }

        .tool-btn {
            width: 40px;
            height: 40px;
            border: none;
            background: transparent;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-sub);
            transition: all 0.2s;
            padding: 0;
        }

        .tool-btn:hover { background: #f3f4f6; color: var(--primary-color); }
        .tool-btn.active { background: var(--primary-color); color: white; }
        
        #handwriting-canvas {
            width: 100%;
            height: 100%;
            display: block;
            touch-action: none;
            cursor: crosshair;
        }

        /* Eraser Specific */
        .tool-btn.eraser-btn:hover,
        .tool-btn.eraser-btn.active {
            background-color: #ffeef0;
            color: #e74c3c !important;
        }
        
        /* Eraser cursor handled by JS (inline style) */

        /* Chat UI */
        #chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            background: #fafafa;
        }

        .chat-message, .bot-message, .user-message {
            max-width: 85%;
            padding: 0.8rem 1.2rem;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            position: relative;
            word-wrap: break-word;
            margin-bottom: 0; /* Controlled by flex gap */
        }
        
        /* Ensure full width overrides */
        .chat-message, .bot-message, .user-message {
             /* Max width logic handled by specific classes below */
        }

        .bot-message {
            align-self: flex-start;
            background: var(--card-bg);
            border: 1px solid #e5e7eb;
            color: var(--text-main);
            border-bottom-left-radius: 4px;
        }

        .user-message {
            align-self: flex-end;
            background: var(--primary-color);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .chat-input-area {
            padding: 1rem;
            background: var(--card-bg);
            border-top: 1px solid #e5e7eb;
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
        }
        
        .chat-input-group {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        #chat-input {
            flex: 1;
            padding: 0.8rem 1.2rem;
            border: 1px solid #e5e7eb;
            border-radius: 99px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
            background: #f9fafb;
        }

        #chat-input:focus {
            border-color: var(--primary-color);
            background: white;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        #chat-send-button {
            background: var(--primary-color);
            color: white;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.1s;
            flex-shrink: 0;
            padding: 0;
        }

        #chat-send-button:active { transform: scale(0.95); }
        #chat-send-button svg { width: 20px; height: 20px; fill: white; }

        /* Helpers */
        .symbol-buttons { display: flex; gap: 5px; justify-content: center; flex-wrap: wrap; }
        .symbol-button { background: #f3f4f6; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; color: var(--text-sub); }
        .symbol-button:hover { background: #e5e7eb; color: var(--text-main); }

        /* Scrollbars */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
    </style>
"""

# ==========================================
# 2. Layout Transformation Logic
# ==========================================

# 2.1 Replace CSS
# Matches everything between first <style> and last </style> (inclusive)
pattern_style = r'<style>.*?</style>'
# If multiple style blocks exist, this greedy match might look scary, but usually index.html has one main block in head.
# To be safe, we match the large block we saw earlier.
# content, count = re.subn(pattern_style, new_css.strip(), content, flags=re.DOTALL)
# Safer: Match from <style> to </style> non-greedily, but replace the distinct block.
# Actually, since we want to overhaul, let's just find the first <style> tag in <head> and replace it.
if "<style>" in content:
    content = re.sub(r'<style>.*?</style>', new_css.strip(), content, count=1, flags=re.DOTALL)
    print("[OK] Replaced CSS.")
else:
    # Insert before </head>
    content = content.replace("</head>", new_css + "\n</head>")
    print("[OK] Inserted CSS.")


# 2.2 Inject Navbar & Fix Main Container
# 檢查 body 結構
if 'class="navbar"' not in content:
    navbar_html = """
    <div class="navbar">
        <h1>📐 Kumon Math AI</h1>
        <div class="user-info">
            <span>Hi, Student</span>
            <a href="/logout">登出</a>
        </div>
    </div>
    """
    # 插入 Navbar 作為 body 的第一個子元素
    # 注意：我們可以找到 <body> 標籤後插入
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + navbar_html, content)
    print("[OK] Injected Navbar.")

# 2.3 Rename Classes for Layout
# <div class="container"> -> <div class="main-container">
if 'class="container"' in content:
    content = content.replace('class="container"', 'class="main-container"')
    print("[OK] Renamed container -> main-container.")

# <div class="practice-area"> -> <div class="left-panel">
if 'class="practice-area"' in content:
    content = content.replace('class="practice-area"', 'class="left-panel"')
    print("[OK] Renamed practice-area -> left-panel.")

# <div class="chat-area"> -> <div class="right-panel">
# 注意：舊 CSS 有 .chat-area { flex: 2; ... }
if 'class="chat-area"' in content:
    content = content.replace('class="chat-area"', 'class="right-panel"')
    print("[OK] Renamed chat-area -> right-panel.")

# 2.4 Add Card Styling
# Add class="card" to #question-container
# Regex to find id="question-container" and append/merge class
# Current: <div class="question-content" id="question-container">
if 'id="question-container"' in content:
    # Check if it has a class attribute
    if 'class="' in re.search(r'<div[^>]*id="question-container"[^>]*>', content).group(0):
        # Append card to existing class
        content = re.sub(r'(<div[^>]*id="question-container"[^>]*class="[^"]*)(")', r'\1 card\2', content)
    else:
        # Add class attribute
        content = content.replace('id="question-container"', 'id="question-container" class="card"')
    print("[OK] Applied .card to question-container.")

# Apply .card to scratchpad
# Current: <div class="practice-bottom" id="scratchpad-container">
# Old CSS .practice-bottom is being replaced by .card + #scratchpad-container styles
if 'id="scratchpad-container"' in content:
    if 'class="' in re.search(r'<div[^>]*id="scratchpad-container"[^>]*>', content).group(0):
        content = re.sub(r'(<div[^>]*id="scratchpad-container"[^>]*class="[^"]*)(")', r'\1 card\2', content)
    else:
        content = content.replace('id="scratchpad-container"', 'id="scratchpad-container" class="card"')
    print("[OK] Applied .card to scratchpad-container.")


# 2.5 Button Icon Replacement (Send Button)
# Find button with id="chat-send-button" and replace text '送出' with Icon
send_icon = """<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>"""
# Pattern: <button id="chat-send-button">送出</button> (allowing whitespace)
# 修正：之前發現文字是 "送出"
pattern_btn = r'(<button[^>]*id="chat-send-button"[^>]*>)\s*(?:送出|Send|發送)\s*(</button>)'
content, count = re.subn(pattern_btn, r'\1' + send_icon + r'\2', content)
if count > 0:
    print(f"[OK] Replaced Send button text with Icon ({count}).")
else:
    print("[Warning] Could not find Send button text.")

# 2.6 Fix specific tool button class if needed
# The user script blindly replaced onclick="setTool...".
# We trust the CSS .tool-btn is sufficient.

# Save
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[Success] Pro UI Upgrade applied.")
