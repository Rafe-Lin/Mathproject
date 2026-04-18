import numpy as np

def poly_to_string(p):
    """將 numpy.poly1d 物件或係數列表轉換為多項式字串"""
    if isinstance(p, (list, tuple)):
        p = np.poly1d(p)
        
    if p.order < 0: return "0"
    terms = []
    for i, c in enumerate(p.coeffs):
        power = p.order - i
        if np.isclose(c, 0): continue
        
        c = int(c) if np.isclose(c, round(c)) else c
        
        coeff_str = f"{c}" if (c != 1 and c != -1) or power == 0 else "" if c==1 else "-"
        var_str = f"x" if power == 1 else f"x{ {2:'²', 3:'³', 4:'⁴', 5:'⁵'}.get(power, f'^{power}') }" if power > 1 else ""
        
        terms.append(f"{coeff_str}{var_str}")
    
    if not terms: return "0"
    return " + ".join(terms).replace("+ -", "- ").lstrip(" +")

def check_answer(user_answer: any, correct_answer: any, check_type: str = 'string') -> dict:
    """
    一個標準化、通用的答案檢查函式，用於比較使用者答案與正確答案。

    這個函式旨在集中處理各種答案的比較邏輯，例如字串、數字或不區分大小寫的
    選項，從而簡化各個技能檔案中的 `check` 函式。
    
    Args:
        user_answer (any): 使用者輸入的原始答案。
        correct_answer (any): 題庫中設定的正確答案。
        check_type (str, optional): 指定答案的比較方式。預設為 'string'。
            可用的選項包括：
            - 'string': 進行精確的字串比對（預設）。
            - 'case_insensitive': 不區分大小寫的比對，適用於選擇題 (A/B/C) 或文字答案。
            - 'numeric': 比較數值，能處理整數與浮點數，並容許微小的浮點數誤差。

    Returns:
        dict: 一個包含檢查結果的字典，格式如下：
              {
                  "correct": bool,      # 答案是否正確
                  "result": str,        # 顯示給使用者的結果文字
                  "next_question": bool # 是否繼續下一題
              }
    """
    user = str(user_answer).strip()
    correct = str(correct_answer).strip()
    is_correct = False

    if check_type == 'case_insensitive':
        # 不區分大小寫比較，適用於選擇題
        is_correct = (user.upper() == correct.upper())
    elif check_type == 'numeric':
        try:
            # 比較浮點數時，使用微小容忍值 (epsilon) 來避免精度問題
            is_correct = abs(float(user) - float(correct)) < 1e-9
        except (ValueError, TypeError):
            # 如果使用者輸入的不是數字，則視為錯誤
            is_correct = False
    else: # 預設為 'string'
        is_correct = (user == correct)

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}