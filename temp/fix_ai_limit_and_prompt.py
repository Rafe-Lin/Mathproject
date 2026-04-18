import os
import re

file_path = os.path.join('core', 'ai_analyzer.py')
if not os.path.exists(file_path):
    # 備用路徑檢查
    file_path = 'ai_analyzer.py'

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在優化 AI 設定：修復截斷問題 + 防止洩漏答案...")

# ==========================================
# 1. 設定適中的 Token 上限 (2048)
# ==========================================
# 我們搜尋 model.generate_content 或是 chat.send_message
# 並插入 generation_config

config_str = ', generation_config={"max_output_tokens": 2048, "temperature": 0.5}'
# temperature 調低一點 (0.5)，讓回答更收斂、更精準，減少廢話

# 檢查是否已經有 generation_config
if "generation_config" in content:
    # 如果已有，用 Regex 替換數值
    # 替換 max_output_tokens
    content = re.sub(r'([\"\']max_output_tokens[\"\']\s*:\s*)\d+', r'\1 2048', content)
    # 替換 temperature
    content = re.sub(r'([\"\']temperature[\"\']\s*:\s*)[\d\.]+', r'\1 0.5', content)
    print("已更新現有的 Token 與 Temperature 設定。")
else:
    # 如果沒有，嘗試注入
    # 針對 generate_content
    pattern_gen = r'(model\.generate_content\s*\(\s*[^,\)]+)(\s*\))'
    content, c1 = re.subn(pattern_gen, r'\1' + config_str + r'\2', content)
    
    # 針對 chat.send_message
    pattern_chat = r'(chat\.send_message\s*\(\s*[^,\)]+)(\s*\))'
    content, c2 = re.subn(pattern_chat, r'\1' + config_str + r'\2', content)
    
    if c1 + c2 > 0:
        print(f"已注入 Token 設定 (共 {c1+c2} 處)。")
    else:
        print("警告：找不到 generate_content/send_message 呼叫點，無法注入 Token 設定。")

# ==========================================
# 2. 注入「防劇透」系統指令
# ==========================================
# 我們要在 Prompt 傳給 AI 之前，或是初始化 Model 時，加強限制。
# 假設程式碼中有定義 PROMPT 變數，或者直接在函數裡組字串。

# 策略：尋找 "System Instruction" 或是在 generate_content 裡的 prompt
# 最通用的方法是：找到所有類似 prompt = "..." 或 f"..." 的地方比較困難
# 我們直接在 generate_content 呼叫前，嘗試注入一段強制的防護詞

# 這裡我們做一個比較通用的防護：
# 在 chat_with_ai (或類似函數) 裡，當使用 user_input 時，強制附加限制詞
# 假設變數名通常叫 prompt 或 user_input 或 message

restrictive_instruction = ' (IMPORTANT: Keep response concise. Do NOT solve the problem. Only guide steps. Do not reveal final answer.)'

# 尋找 chat.send_message(message) 或类似
# 我們把 message 替換成 (message + "指令")
pattern_msg = r'chat\.send_message\s*\(\s*([a-zA-Z_0-9]+)\s*'

def replace_msg(match):
    var_name = match.group(1)
    # 排除已經是字串的情況，只處理變數
    if var_name in ['prompt', 'message', 'text', 'user_input']:
        return f'chat.send_message({var_name} + "{restrictive_instruction}"'
    return match.group(0)

content, c3 = re.subn(pattern_msg, replace_msg, content)

if c3 > 0:
    print(f"已在 {c3} 處對話邏輯中加入「禁止直接給答案」的指令。")
else:
    # 嘗試另一種模式：model.generate_content(prompt)
    pattern_gen_prompt = r'model\.generate_content\s*\(\s*([a-zA-Z_0-9]+)\s*'
    content, c4 = re.subn(pattern_gen_prompt, replace_msg, content)
    if c4 > 0:
        print(f"已在 {c4} 處生成邏輯中加入「禁止直接給答案」的指令。")

# ==========================================
# 3. 增加 response.text 的防呆保護 (同上一步，確保穩定)
# ==========================================
safe_text_logic = """
    if not response.candidates or not response.parts:
        return "{}" 
    return response.text
"""
pattern_return = r'(\s+)return\s+response\.text'
match = re.search(pattern_return, content)
if match:
    indent = match.group(1)
    formatted_logic = safe_text_logic.replace('\n    ', '\n' + indent)
    content = re.sub(pattern_return, formatted_logic, content, count=1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("優化完成！\n1. Token 設為 2048 (防崩潰)\n2. Temperature 降為 0.5 (更冷靜)\n3. 增加 Prompt 後綴指令 (防劇透)")
