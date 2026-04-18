import os

file_path = os.path.join('templates', 'index.html')
if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在進行視覺風格升級 (CSS Only)...")

# 定義要注入的新 CSS
# 包含 :root 變數、兩套主題、以及各元件的美化規則
css_upgrade = """
    <!-- ========================================================================== -->
    <!-- VISUAL UPGRADE: Professional, Natural, Reliable, Cute & Cultural           -->
    <!-- ========================================================================== -->
    <style>
    :root {
        /* --- 預設主題 (自然、可靠、穩重 - Natural & Reliable) --- */
        /* 色票來源：北歐森林與大地色系 */
        --primary-color: #2D6A4F;      /* 深翠綠 - 專業與信任 */
        --secondary-color: #40916C;    /* 中綠色 - 自然 */
        --accent-color: #D8F3DC;       /* 淺薄荷 - 柔和背景 */
        --highlight-color: #95D5B2;    /* 亮綠色 - 強調 */
        
        --action-color: #1B4332;       /* 極深綠 - 按鈕/文字 */
        --warn-color: #E07A5F;         /* 柔和紅 - 錯誤/警告 */
        
        --bg-color: #F8F9FA;           /* 雲朵白 - 整體背景 */
        --card-bg: #FFFFFF;            /* 純白 - 卡片背景 */
        
        --text-main: #1F2937;          /* 炭灰 - 主要文字 */
        --text-sub: #6B7280;           /* 灰 - 次要文字 */

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 20px;
        --radius-xl: 30px;             /* 用於按鈕與聊天氣泡 */
        
        /* 陰影系統 (Neumorphism 輕量化) */
        --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-sm: 0 2px 4px rgba(45,106,79,0.08);
        --shadow-md: 0 4px 12px rgba(45,106,79,0.12);
        --shadow-lg: 0 10px 25px rgba(45,106,79,0.15);
        
        --font-main: "Nunito", "Segoe UI", "Microsoft JhengHei", system-ui, sans-serif;
    }

    /* --- 文青可愛主題 (可透過 class="theme-cute" 切換) --- */
    body.theme-cute {
        --primary-color: #F4A261;      /* 溫暖橘 */
        --secondary-color: #E9C46A;    /* 芥末黃 */
        --accent-color: #FEFAE0;       /* 米白 */
        --action-color: #264653;       /* 深藍綠 */
        --bg-color: #FAF3DD;           /* 復古紙張色 */
    }

    /* === 全局基礎優化 === */
    body {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
        font-family: var(--font-main) !important;
        letter-spacing: 0.02em; /* 增加一點點字距，閱讀更舒適 */
    }

    /* === Navbar 升級 === */
    .navbar {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        box-shadow: var(--shadow-md) !important;
        border-bottom: none !important;
    }
    .navbar .logo {
        color: white !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .navbar a {
        background: rgba(255,255,255,0.1) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(5px);
    }
    .navbar a:hover {
        background: rgba(255,255,255,0.25) !important;
        transform: translateY(-1px);
    }

    /* === 卡片區塊 (練習區 & 聊天區) === */
    .practice-area, .chat-area {
        border: none !important;  /* 移除舊邊框 */
        background: transparent !important; /* 讓容器透出背景，我們只對內部卡片上色 */
    }

    /* 真正的卡片實體 */
    #question-container, #scratchpad-container, #chat-history {
        background-color: var(--card-bg) !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-md) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    #question-container:hover, #scratchpad-container:hover, #chat-history:hover {
        box-shadow: var(--shadow-lg) !important;
    }

    /* === 按鈕全域升級 (Interactive Solid Style) === */
    /* 1. 主要操作按鈕 */
    #submit-button, #chat-send-button, #practice-prereq-btn {
        background: var(--action-color) !important;
        color: white !important;
        border-radius: var(--radius-md) !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 0 rgba(0,0,0,0.2); /* 3D 按壓感 */
        transform: translateY(0);
        transition: all 0.15s ease !important;
        border: none !important;
    }
    #submit-button:hover, #chat-send-button:hover, #practice-prereq-btn:hover {
        background-color: var(--primary-color) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 0 rgba(0,0,0,0.2);
    }
    #submit-button:active, #chat-send-button:active, #practice-prereq-btn:active {
        transform: translateY(2px);
        box-shadow: 0 2px 0 rgba(0,0,0,0.2);
    }

    /* 2. 工具按鈕 (Tool Buttons) */
    .tool-btn, .level-button, .symbol-button {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-sub) !important;
        box-shadow: var(--shadow-xs) !important;
        font-weight: 600;
    }
    .tool-btn:hover, .level-button:hover, .symbol-button:hover {
        border-color: var(--secondary-color) !important;
        color: var(--primary-color) !important;
        background-color: var(--accent-color) !important;
        transform: translateY(-1px);
    }
    .tool-btn.active, .level-button.active {
        background-color: var(--secondary-color) !important;
        color: white !important;
        border-color: var(--secondary-color) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* === 輸入框 (Soft Input) === */
    input[type="text"], #answer-input, #chat-input {
        background-color: #F3F4F6 !important;
        border: 2px solid transparent !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: var(--text-main) !important;
        transition:all 0.3s ease;
    }
    input[type="text"]:focus, #answer-input:focus, #chat-input:focus {
        background-color: white !important;
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 0 4px var(--accent-color) !important;
        outline: none !important;
    }

    /* === 聊天室視覺 (Bubble Style) === */
    /* AI 頭像/標題區 */
    .chat-area h3 {
        color: var(--primary-color) !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }

    /* AI 訊息氣泡 */
    .bot-message, .initial-bot-message {
        background: #FFFFFF !important;
        border: 1px solid #F0F0F0 !important;
        border-radius: 0 var(--radius-xl) var(--radius-xl) var(--radius-xl) !important; /* 左上角尖角 */
        box-shadow: var(--shadow-sm) !important;
        color: var(--text-main) !important;
    }
    /* 初始訊息特別加強 */
    .initial-bot-message {
        border: 2px solid var(--secondary-color) !important;
        background-color: var(--accent-color) !important;
        color: var(--action-color) !important;
        font-weight: bold;
    }

    /* 使用者訊息氣泡 */
    .user-message {
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color)) !important;
        color: white !important;
        border-radius: var(--radius-xl) 0 var(--radius-xl) var(--radius-xl) !important; /* 右上角尖角 */
        box-shadow: var(--shadow-md) !important;
    }

    /* 提示詞按鈕 (Chips) */
    .suggestion-btn, .prompt-button {
        background-color: white !important;
        border: 1px solid var(--secondary-color) !important;
        color: var(--secondary-color) !important;
        border-radius: 50px !important; /* Pill shape */
        padding: 5px 15px !important;
        font-size: 0.9em !important;
        box-shadow: var(--shadow-xs) !important;
    }
    .suggestion-btn:hover, .prompt-button:hover {
        background-color: var(--secondary-color) !important;
        color: white !important;
        transform: scale(1.05);
        box-shadow: var(--shadow-md) !important;
    }

    /* 字體大小控制按鈕 */
    .font-controls button {
        border-color: var(--secondary-color) !important;
        color: var(--secondary-color) !important;
    }
    .font-controls button:hover {
        background: var(--secondary-color) !important;
        color: white !important;
    }

    /* === 捲軸美化 (Natural Scroll) === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F1F1F1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: #C1C1C1;
        border-radius: 4px;
        border: 2px solid #F1F1F1; /* 創造懸浮感 */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-color);
    }
    </style>
"""

# 將 CSS 插入到 </body> 之前，確保覆蓋所有先前的樣式
if "</body>" in content:
    content = content.replace("</body>", css_upgrade + "\n</body>")
    print("已注入高質感 CSS 樣式 (Natural & Reliable Theme)。")
else:
    # 備用方案：如果沒有 body tag，就加在檔案最後
    content += css_upgrade
    print("找不到 </body>，已將 CSS 附加至檔案末尾。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("視覺升級完成！請重新整理網頁體驗新風格。")
