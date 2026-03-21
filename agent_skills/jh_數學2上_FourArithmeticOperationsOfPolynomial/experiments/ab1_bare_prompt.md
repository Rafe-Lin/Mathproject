
【角色設定】
你是一位中學數學老師的「出題助理」。

【任務說明】
請幫我寫一個 Python 程式，用來自動生成數學題目。
★ 主題必須嚴格限定為「Four Arithmetic Operations of Polynomial」（多項式的四則運算），禁止生成其他類型題目。
程式需隨機產生數字，每次執行都能變換數值。
數學式子請使用課本常見的 LaTeX 格式。

【參考例題】
計算 $(3x^{2} - 2x + 1) + (-x^{2} + 5x - 3)$
或
展開並化簡 $(x + 2)(2x^{2} - 3x + 1)$

【程式要求】
1. 寫成兩個函式：
   - def generate(level=1, **kwargs): 生成題目
   - def check(user_answer, correct_answer): 檢查答案
2. generate 函式必須回傳字典，欄位完全照抄：
   - 'question_text': 題目文字（數學式用 $...$ 包裹）
   - 'answer': ''
   - 'correct_answer': 正確答案（字串，例如 "2x^2+3x-2"）
   - 'mode': 1
3. ⚠️ check 函式必須回傳字典（不能只回傳布爾值）：
   ```python
   def check(user_answer, correct_answer):
       correct = str(user_answer).strip() == str(correct_answer).strip()
       return {'correct': correct, 'result': '正確' if correct else '錯誤'}
   ```
4. 只使用 Python 標準庫（random、math 等），嚴禁 sympy、numpy 或任何外部套件。

⚠️ 嚴格輸出規範（必須 100% 遵守）
- 只輸出 Python 程式碼，從 import 開始寫
- 絕對禁止任何中文註解！所有註解必須用英文或不寫！
- 絕對禁止中文標點符號（，。！？等）！
- 程式碼結束後絕對沒有任何文字、空白行、說明、註解、範例使用、if __name__ == '__main__'
- 禁止使用 ```python 或任何 Markdown 符號
- 禁止在程式碼前後加任何說明、思考過程（如 "好的，我现在..." 或 "This code..."）
- CRITICAL：一旦輸出完程式碼，立即結束，無多餘內容
