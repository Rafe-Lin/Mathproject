【角色設定】
你是一位中學數學老師的「出題助理」。

【任務說明】
請幫我寫一個 Python 程式，用來自動生成數學題目。
★ 題目主題必須是：「整數的四則運算」（請務必嚴格針對此主題出題，禁止生成其他類型的題目）
這個程式需要隨機產生數字，每次執行都能變換數值。
請使用跟課本一樣的格式表達數學式子。

【參考例題】【參考例題】{{OCR_RESULT}}

【程式要求】
1. 請寫成兩個函式：
   - def generate(level=1, **kwargs): 生成題目
   - def check(user_answer, correct_answer): 檢查答案是否正確
2. generate 函式要回傳一個字典，包含以下欄位（請照抄 key 名稱）：
   - 'question_text': 題目文字
   - 'answer': 空字串 ''
   - 'correct_answer': 正確答案（必須是整數字串，例如 "39" 或 "-15"）
   - 'mode': 1
3. check 函式要回傳一個字典，包含：
   - 'correct': True 或 False
   - 'result': '正確' 或 '錯誤'
4. 請只使用 Python 標準庫（如 random, math），嚴禁使用 sympy、numpy 或任何外部套件。

⚠️ 重要：只輸出 Python 程式碼！
- 正確：直接從 import 開始寫
- 錯誤：不要加任何說明文字、註解、範例使用、if __name__ == '__main__'
- 錯誤：不要用 ```python 或任何 Markdown 符號包裹代碼
- 錯誤：不要在程式碼前後加任何文字（包括空白行後的說明）
- CRITICAL：程式碼結束後絕對無任何額外內容
