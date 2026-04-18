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

print("正在執行 AI 穩定性修復 v2 (Token 擴容 + 語法強化)...")

# ==========================================
# 1. 提升 Token 上限 (2048 -> 4096)
# ==========================================
# 尋找上次設定的 max_output_tokens: 2048
# 直接改成 4096

if "\"max_output_tokens\": 2048" in content:
    content = content.replace("\"max_output_tokens\": 2048", "\"max_output_tokens\": 4096")
    print("已將 Token 上限提升至 4096。")
elif "\"max_output_tokens\": 8192" in content:
    print("Token 已經是 8192，無需調整。")
else:
    # 如果找不到，可能是格式問題，嘗試用 Regex 暴力替換任何數字
    content = re.sub(r'(\"max_output_tokens\"\s*:\s*)\d+', r'\1 4096', content)
    print("已強制更新 Token 設定為 4096。")

# ==========================================
# 2. 強化 Prompt (要求正確的 JSON 跳脫)
# ==========================================
# 我們要告訴 AI：在 JSON 字串裡，LaTeX 的 \ 必須寫成 \\
# 尋找我們上次加的 LaTeX 指令

old_latex_instruction = "Use LaTeX format for all math expressions (surround with $). Example: $x^2$."
# 新指令：增加 "Double escape backslashes"
new_latex_instruction = "Use LaTeX format (surround with $). IMPORTANT: Escape all backslashes in JSON (e.g. use \\\\frac instead of \\frac)."

if old_latex_instruction in content:
    content = content.replace(old_latex_instruction, new_latex_instruction)
    print("已更新系統指令：要求雙重跳脫反斜線 (Double Escape)。")
else:
    # 如果找不到完全匹配的字串，嘗試尋找 Prompt 結尾注入
    print("找不到舊指令，嘗試在 Prompt 尾端注入新規則...")
    # 尋找任何 "Do not reveal final answer." 這是我們上次加的
    anchor = "Do not reveal final answer."
    if anchor in content:
        # 在它後面加上新指令
        content = content.replace(anchor, anchor + " " + new_latex_instruction)
        print("已補上 JSON 跳脫規則。")

# ==========================================
# 3. 寫回檔案
# ==========================================
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("修復完成！請重啟伺服器。這次應該穩了！")
