import os

file_path = os.path.join('core', 'ai_analyzer.py')
if not os.path.exists(file_path):
    file_path = 'ai_analyzer.py'

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在更新 AI 指令：強制要求使用 LaTeX 數學排版...")

# 這是我們上一部加入的指令片段
old_instruction = "Do NOT solve the problem. Only guide steps. Do not reveal final answer."

# 這是我們想加入的新指令 (要求用 $ 包裹 LaTeX)
latex_instruction = " Use LaTeX format for all math expressions (surround with $). Example: $x^2$."

# 組合新的完整指令
new_instruction = old_instruction + latex_instruction

# 執行替換
if old_instruction in content:
    # 檢查是否已經加過了，避免重複疊加
    if latex_instruction in content:
        print("檢測到指令中似乎已經包含 LaTeX 要求，無需修改。")
    else:
        content = content.replace(old_instruction, new_instruction)
        print("已成功將 LaTeX 排版要求加入 AI 的系統指令中。")
else:
    # 如果找不到上一部的指令 (極少見情況)，我們嘗試尋找 send_message 直接注入
    print("找不到前次設定的指令片段，嘗試直接尋找發送點...")
    import re
    # 尋找 chat.send_message(變數 + "...") 的結構
    pattern = r'(chat\.send_message\([^\)]+)(\"\))' 
    # 這裡假設程式碼現在長這樣: chat.send_message(user_input + "... Do not reveal final answer.")
    
    match = re.search(pattern, content)
    if match:
        # 在結尾引號前插入 LaTeX 指令
        insertion = latex_instruction
        content = re.sub(pattern, r'\1' + insertion + r'\2', content)
        print("已強制注入 LaTeX 指令。")
    else:
        print("無法自動定位注入點，請確認是否已執行過上一步驟 (fix_ai_limit_and_prompt.py)。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("完成！現在 AI 回答數學問題時，會自動使用漂亮的 LaTeX 格式了 (例如 $x^2$)。")
