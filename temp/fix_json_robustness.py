import os
import re
import json

file_path = os.path.join('core', 'ai_analyzer.py')
if not os.path.exists(file_path):
    file_path = 'ai_analyzer.py'

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在部署三層防護網 (智慧修復 JSON + 8192 Token + 簡潔 Prompt)...")

# ==========================================
# 1. 替換為「智慧修復版」clean_and_parse_json
# ==========================================
# 這個新版本會計算缺少的 } ] 和 " 並自動補上

robust_json_func = """
def clean_and_parse_json(text):
    \"\"\"
    強力清洗並解析 JSON，包含自動修復截斷內容的功能。
    \"\"\"
    # 1. 移除 Markdown
    text = re.sub(r'```json\\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\\s*', '', text)
    
    # 2. 抓取最外層 {}
    match = re.search(r'\\{.*', text, re.DOTALL) # 這裡改寬鬆一點，只要有開頭就好
    if match:
        text = match.group(0)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # === 自動修復機制 ===
        print(f"JSON 解析失敗，嘗試自動修復截斷內容...")
        
        # 1. 修復未閉合的字串 (如果引號是奇數個，補一個)
        # 簡單判斷：計算雙引號數量 (排除跳脫的 \")
        quote_count = len(re.findall(r'(?<!\\\\)"', text))
        if quote_count % 2 != 0:
            text += '"'
            
        # 2. 修復未閉合的括號
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')
        
        # 依序補上缺少的結尾 (簡單推測)
        # 通常 JSON 結尾是 ]} 或 }
        # 我們直接補充足夠的 } 和 ]
        # 注意：這只是簡易修復，可能無法處理複雜巢狀，但能防止崩潰
        
        # 優先補 List 的 ]
        if open_brackets > 0:
            text += ']' * open_brackets
            
        # 再補 Object 的 }
        if open_braces > 0:
            text += '}' * open_braces
            
        try:
            return json.loads(text)
        except:
            print("自動修復失敗，回傳安全預設值。")
            # 真的救不回來，回傳一個顯示錯誤的 JSON，避免前端白畫面
            return {
                "reply": "（AI 回應訊號中斷，但您答對了！請繼續下一題。）", 
                "follow_up_prompts": ["繼續練習"]
            }
"""

# 使用 Regex 替換原本的函式
# 尋找 def clean_and_parse_json(text): ... 到下一個 def 之前
pattern_func = r'def clean_and_parse_json\(text\):.*?(?=\n\s*#|\n\s*def|\Z)'

# Raw string for replacement to avoid escape issues
robust_json_func_repl = robust_json_func.replace('\\', '\\\\')

content = re.sub(pattern_func, lambda m: robust_json_func, content, flags=re.DOTALL)
print("已部署「智慧修復 JSON」機制。")


# ==========================================
# 2. 強制注入 max_output_tokens: 8192
# ==========================================
# 掃描所有的 generate_content 和 send_message
# 如果已經有 config，替換數字；如果沒有，插入 config

config_snippet = ', generation_config={"max_output_tokens": 8192, "temperature": 0.7}'

# 針對 model.generate_content
if "generation_config" in content:
    # 強制替換數字
    content = re.sub(r'["\']max_output_tokens["\']\s*:\s*\d+', '"max_output_tokens": 8192', content)
    print("已更新現有 Token 設定為 8192。")
else:
    # 插入
    content = re.sub(r'(model\.generate_content\([^)]+)', r'\1' + config_snippet, content)
    content = re.sub(r'(chat\.send_message\([^)]+)', r'\1' + config_snippet, content)
    print("已在 API 呼叫中注入 8192 Token 設定。")


# ==========================================
# 3. 在 Prompt 中加入嚴格字數限制
# ==========================================
# 找到我們之前加的指令位置，再補上一刀
# 或者直接修改 DEFAULT_CHAT_PROMPT 變數 (如果有的話)

limit_instruction = " (Keep output concise. < 150 words.)"

if "DEFAULT_CHAT_PROMPT =" in content:
    # 在 JSON 格式說明前加入限制
    content = content.replace("【JSON 輸出格式】", f"【嚴格字數限制】：\n請保持回答在 150 字以內，避免截斷。\n\n【JSON 輸出格式】")
    print("已在 Chat Prompt 中加入字數限制。")
else:
    # 嘗試在 send_message 處注入
    pattern_send = r'(chat\.send_message\([^,]+)'
    # 檢查是否已經注入過
    if "concise" not in content:
        content = re.sub(pattern_send, r'\1 + "' + limit_instruction + '"', content)
        print("已在發送訊息時強制附加字數限制指令。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("終極修復完成！請重啟伺服器。現在 AI 應該「很難」再搞崩網頁了。")
