import os
import re

file_path = os.path.join('core', 'ai_analyzer.py')
if not os.path.exists(file_path):
    file_path = 'ai_analyzer.py'

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在修復 NameError: gemini_chat 未定義的問題...")

# ==========================================
# 1. 在全域範圍宣告 gemini_chat
# ==========================================
# 尋找 gemini_model = None，在下面補上 gemini_chat = None
if "gemini_chat = None" not in content:
    content = content.replace("gemini_model = None", "gemini_model = None\ngemini_chat = None")
    print("[OK] 已宣告全域變數 gemini_chat。")

# ==========================================
# 2. 在 configure_gemini 中初始化
# ==========================================
# 找到 def configure_gemini(...):
# 確保裡面有 global gemini_chat
# 並且執行 gemini_chat = gemini_model.start_chat(history=[])

def update_configure_gemini(match):
    func_body = match.group(0)
    
    # 1. 加入 global 宣告
    if "global gemini_chat" not in func_body:
        # 簡單插入：在 global gemini_model 後面加
        func_body = func_body.replace("global gemini_model", "global gemini_model, gemini_chat")
    
    # 2. 初始化 start_chat
    # 在 gemini_model = genai.GenerativeModel(...) 之後插入
    # 我們尋找設定 model 的那一行
    if "gemini_chat = gemini_model.start_chat" not in func_body:
        # 尋找 gemini_model 初始化完成的地方
        init_pattern = r'(gemini_model\s*=\s*genai\.GenerativeModel\([^\)]+\))'
        # 插入初始化代碼
        func_body = re.sub(init_pattern, r'\1\n    gemini_chat = gemini_model.start_chat(history=[])', func_body)
    
    return func_body

# 使用 Regex 捕捉整個 configure_gemini 函數 (假設縮排結構正常)
# 這裡簡單抓取函數頭部到結尾不太容易，我們直接針對關鍵字插入
# 策略：直接替換 configure_gemini 的定義內容.
# 但是因為我們沒有用 update_configure_gemini 函數，直接用 re.sub string replace 吧。

if "def configure_gemini" in content:
    # 1. 補 global
    if "global gemini_chat" not in content:
        content = content.replace("global gemini_model", "global gemini_model, gemini_chat")
    
    # 2. 補初始化 (如果還沒初始化)
    if "gemini_chat = gemini_model.start_chat" not in content:
        # 找到 gemini_model = ... 的下一行
        # 注意：這裡假設代碼中有 gemini_model = genai.GenerativeModel(...)
        pattern_model_init = r'(gemini_model\s*=\s*genai\.GenerativeModel\s*\([^\)]+\))'
        content = re.sub(pattern_model_init, r'\1\n    gemini_chat = gemini_model.start_chat(history=[])', content)
        print("[OK] 已在 configure_gemini 中初始化 gemini_chat。")

# ==========================================
# 3. 檢查使用點 (get_chat_response)
# ==========================================
# 防止在使用時 gemini_chat 還是 None
# 我們在 get_chat_response (或類似函數) 開頭加入檢查

check_code = """
    global gemini_chat
    if gemini_chat is None and gemini_model is not None:
        gemini_chat = gemini_model.start_chat(history=[])
"""

# 尋找函數定義 (假設函數名是 get_chat_response 或 ask_ai_text)
# 我們嘗試在呼叫 gemini_chat.send_message 之前插入檢查
# 但最穩妥的是在函數開頭加

if "def get_chat_response" in content:
    pattern_func = r'(def get_chat_response\s*\([^)]*\)\s*:)'
    # 在函數定義後插入檢查代碼
    content = re.sub(pattern_func, r'\1' + check_code, content)
    print("[OK] 已加入 gemini_chat 防呆檢查 (get_chat_response)。")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[DONE] 修復完成！gemini_chat 變數已正確定義與初始化。")
