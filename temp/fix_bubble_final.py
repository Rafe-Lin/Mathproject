
import os
import re

# 1. 設定檔案路徑
file_path = os.path.join('templates', 'index.html')

if not os.path.exists(file_path):
    print(f"錯誤: 找不到 {file_path}")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("正在修正灰色氣泡寬度...")

# 2. 精準鎖定並替換
# 策略：直接尋找 CSS 中的 max-width: 80%; 並將其替換掉
# 這是最根源的解法，比覆蓋更有效

# 情況 A: 針對 .chat-message 的修改
# 我們尋找包含 max-width: 80% 的字串 (允許分號前後有空格)
pattern = r'max-width:\s*80%;'
replacement = 'max-width: 100%; width: 100%; box-sizing: border-box;'

# 執行全域替換 (防止有漏網之魚)
new_content, count = re.subn(pattern, replacement, content)

if count > 0:
    print(f"[OK] 成功！找到了 {count} 處「80%」的限制，已全部改為「100%」。")
else:
    print("[Warning] 警告：找不到 'max-width: 80%;'，嘗試暴力強制覆蓋...")
    
    # 情況 B: 如果原始碼寫法不同 (例如寫在 style 屬性或其他格式)，則使用核彈級覆蓋
    # 在 <head> 的 <style> 最後面插入最強樣式
    override_css = """
        /* 強制灰色氣泡滿版 */
        .chat-message, .chat-ai, .chat-user {
            max-width: 100% !important;
            width: 100% !important;
            min-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            box-sizing: border-box !important;
        }
    """
    if "</style>" in new_content:
        new_content = new_content.replace("</style>", override_css + "\n</style>")
        print("[OK] 已植入 !important 強制樣式來覆寫設定。")

# 3. 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[Success] 修正完成！灰色氣泡現在應該會填滿整個框框了。")
