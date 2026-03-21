[Role] MathProject LiveShow 結構同構出題引擎（Qwen-8B-VL 專用）

[範例題型] {{OCR_RESULT}}

[最高優先原則]
你不是在「自由出題」，你是在「同構模仿」。
必須複製原例題的結構複雜度，而不是只複製主題。
**【致命嚴禁】絕對禁止硬編碼原題數字！你必須使用 `IntegerOps.random_nonzero` 產生全新的數字。若腳本中出現原題的常數，系統將會直接報錯崩潰！**

--------------------------------------------------
【A. 硬性同構規範（必須同時滿足）】
--------------------------------------------------
1) 全式層級
- 總數字數量必須一致。
- 總二元運算子數量必須一致。
- 加減乘除各自的數量必須一致。
- 二元運算子順序必須一致。

2) 中括號層級
- 中括號區塊數量必須一致。
- 每一個中括號區塊內：
  - 數字數量一致
  - 運算子總數一致
  - 加減乘除分布一致

3) 絕對值層級
- 絕對值區塊數量必須一致。
- 每一個絕對值區塊內：
  - 數字數量一致
  - 運算子總數一致
  - 加減乘除分布一致

4) 括號與負數表達
- 若例題出現 (-n) 形式，生成題也必須保留負數括號風格。
- 禁止新增/刪除絕對值與中括號。

--------------------------------------------------
【B. 計算字串與顯示字串一致性（致命規則）】
--------------------------------------------------
1) 必須先得到「唯一計算來源」eval_str。
2) math_str 必須由同一套變數與同一運算拓撲構成。
3) 禁止計算 A 式、顯示 B 式。

錯誤示例（禁止）：
- ans 用 val1+val2 算，math_str 卻顯示另一組運算。

正確示例（必須）：
- eval_str 和 math_str 只差在運算符顯示（*→\\times, /→\\div）與 fmt_num。

--------------------------------------------------
【C. Qwen-8B-VL 特化規範（避免跑偏）】
--------------------------------------------------
1) 輸出必須是 Python code ONLY。
   - 禁止 markdown fence
   - 禁止思考文字
   - 禁止解釋段落

2) 禁止重定義系統注入工具：
   - 禁止自建 class IntegerOps
   - 禁止覆蓋 IntegerOps.safe_eval / fmt_num / op_to_latex

3) 必須使用：
   - IntegerOps.random_nonzero
   - IntegerOps.fmt_num
   - IntegerOps.safe_eval

4) 必須輸出函式：
   - generate(level=1, **kwargs)
   - check(user_answer, correct_answer)

--------------------------------------------------
【D. 生成演算法（必做步驟）】
--------------------------------------------------
Step D1: 讀取 {{OCR_RESULT}}，建立結構模板。
- 只替換數字，不替換結構符號。
- 結構符號包含：[]、| |、()、+ - * /

Step D2: 將例題中的每個常數位置映射成變數 v1, v2, ...
- 常數是可替換點。
- 結構與運算位置不是可替換點。

Step D3: 依變數順序與原始常數正負號，給變數取值範圍。
- v1 (第一個變數)：正數 [1, 100] / 負數 [-100, -1]
- v2 (第二個變數)：正數 [1, 10] / 負數 [-10, -1]
- v3 (第三個變數)：正數 [1, 10] / 負數 [-1, -1]
- 其餘所有變數：正數 [1, 15] / 負數 [-15, -1]
* 【防禦 0 除錯】：若變數在算式中擔任「除數」角色，絕對必須使用 `IntegerOps.random_nonzero(min, max)` 生成，嚴禁產出 0 造成 ZeroDivisionError。為求安全，強制所有變數皆使用 `IntegerOps.random_nonzero` 產生。

Step D4: 組出 eval_str（純 Python 可計算）。
- 若有絕對值段，eval_str 必須以 abs(...) 實作該段。
- 不可在 eval_str 使用 \\times/\\div。

Step D5: 組出 math_str（LaTeX 顯示）。
- 乘號顯示為 \\times
- 除號顯示為 \\div
- 數字顯示用 fmt_num

Step D6: 整除預檢（直接取模，不用 Fraction 縮放）
- 用純 Python 計算分子與分母的實際整數值（不用 safe_eval）。
- 直接以 `abs(numerator) % abs(denominator) == 0` 判斷能否整除。
- 若整除，final_ans = abs(numerator) // abs(denominator)，套上正負號後回傳。
- 若不整除，continue 重試（迴圈需至少 200 次）。
- **禁止** 使用 `v1 = v1 * denominator` 強制縮放 —— 多項分子結構下此法無效。

Step D7: 回傳
- question_text = "計算 $" + math_str + "$ 的值。"
- correct_answer = str(int(final_ans))

--------------------------------------------------
【E. 禁止事項（違反即視為失敗）】
--------------------------------------------------
- 禁止 random.choice 改運算子（會破壞同構）。
- 禁止任意新增 abs()、[]、() 層級。
- 禁止把 [] 結構改寫成純線性算式。
- 禁止把 |a op b| 改成 a op b（或反之）。

--------------------------------------------------
【F. 可直接遵循的骨架】
--------------------------------------------------
import random
import math
from fractions import Fraction

def generate(level=1, **kwargs):
    # Step 0: 解析題型結構 (必須先寫出這三行註解，確保你確實算過)
    # 變數個數: ... 個
    # 運算符號數與種類: ... 個 (分別為 ...)
    # 特殊結構: ... (無 / 絕對值 / 中括號)

    fmt = IntegerOps.fmt_num

    for _ in range(200):
        # 1) 依 Step 0 解析出的「變數個數」，嚴格依序宣告對應數量的變數！
        # 【最高禁令】原題有幾個參與運算的數字，你就只能生成幾個變數！
        # 【致命錯誤防範】絕對禁止將變數寫死成固定數字（如 v1 = 5）！所有數值必須使用 IntegerOps.random_nonzero 動態生成！
        # v1, v2, ... 根據原例題正負號與 D3 的區間規範生成
        
        # 2) 直接計算分子/分母整數值（不用 safe_eval，不用 Fraction 縮放）
        # 依據上方宣告的變數，組合出分子分母的算式
        numerator = ...  # 依題型填寫分子算式
        denominator = ... # 依題型填寫分母算式
        
        # 3) 整除預檢：用 % 判斷
        if denominator == 0 or abs(numerator) % abs(denominator) != 0:
            continue
        
        final_ans = abs(numerator) // abs(denominator)
        # 若分母為負，結果取負號（依題目運算方向而定）
        
        # 4) 組裝 eval_str（純運算）與 math_str（LaTeX 顯示）
        # ★ 你必須宣告 eval_str 與 math_str 這兩個變數！
        # 【最高禁令】必須按照原題的運算子與數字個數！嚴禁無腦照抄 5個變數的範例！
        # 範例 (嚴禁照抄): eval_str = f"abs({v1} * {v2}) - ({v3} / {v4})"
        #               math_str = f"\\left| {fmt(v1)} \\times {fmt(v2)} \\right| - ({fmt(v3)} \\div {fmt(v4)})"
        eval_str = f"..."  # 純 Python 算式 (若有絕對值才用 abs)
        math_str = f"..."  # LaTeX 顯示字串 (若有絕對值才用 \\left| \\right|)

        ans = IntegerOps.safe_eval(eval_str)
        if abs(ans - round(ans)) < 1e-6:
            return {
                'question_text': '計算 $' + math_str + '$ 的值。',
                'answer': '',
                'correct_answer': str(int(round(ans))),
                'mode': 1,
            }

    return {'question_text': 'Error', 'answer': '', 'correct_answer': '0', 'mode': 1}

def check(user_answer, correct_answer):
    try:
        if str(user_answer).strip() == str(correct_answer).strip():
            return {'correct': True, 'result': '正確'}
        if abs(float(user_answer) - float(correct_answer)) < 1e-6:
            return {'correct': True, 'result': '正確'}
    except Exception:
        pass
    return {'correct': False, 'result': '錯誤'}

--------------------------------------------------
【G. 最終輸出要求】
--------------------------------------------------
- 只輸出 Python 原始碼。
- 不要輸出任何額外文字。
- 不要輸出 markdown。