# skills/abs_val_eq.py
import random

def format_linear_expression(a, b):
    """格式化線性表達式 ax + b"""
    if a == 0:
        return str(b) if b != 0 else "0"
    
    # 處理 x 的係數
    if a == 1:
        x_term = "x"
    elif a == -1:
        x_term = "-x"
    else:
        x_term = f"{a}x"
    
    # 處理常數項
    if b == 0:
        return x_term
    elif b > 0:
        return f"{x_term} + {b}"
    else:
        return f"{x_term} - {abs(b)}"

def generate(level=1):
    """生成「絕對值方程式」題目"""
    question_type = random.choice([
        'simple_abs',           # 簡單形式 |x| = c
        'linear_abs_specific',  # |ax + b| = c，求特定解（較大或較小）
        'linear_abs_any'        # |ax + b| = c，求任一解
    ])
    # level 參數暫時未使用，但保留以符合架構
    
    if question_type == 'simple_abs':
        # 簡單形式 |x| = c（圖形題，兩個答案）
        c = random.randint(1, 10)
        
        question_text = (
            f"請在下方的「數位計算紙」上，解絕對值方程式：|x| = {c}\n\n"
            f"請在數線上標示出所有解，畫完後，請點擊「AI 檢查」按鈕。"
        )
        context_string = f"解絕對值方程式 |x| = {c}，在數線上標示所有解"
        
        return {
            "question_text": question_text,
            "answer": None,
            "correct_answer": "graph",
            "context_string": context_string
        }
    
    elif question_type == 'linear_abs_specific':
        # |ax + b| = c，求特定解
        a = random.choice([1, -1, 2, -2, 3, -3])
        b = random.randint(-5, 5)
        c = random.randint(1, 8)
        
        # 計算兩個解
        # ax + b = c 或 ax + b = -c
        # x = (c - b) / a 或 x = (-c - b) / a
        sol1 = (c - b) / a
        sol2 = (-c - b) / a
        
        # 簡化顯示
        if sol1 == int(sol1):
            sol1 = int(sol1)
        else:
            sol1 = round(sol1, 2)
        if sol2 == int(sol2):
            sol2 = int(sol2)
        else:
            sol2 = round(sol2, 2)
        
        # 確保 sol1 和 sol2 不同
        if abs(sol1 - sol2) < 0.01:
            # 如果相同，重新生成
            return generate()
        
        # 決定要求較大還是較小的解
        if sol1 > sol2:
            larger, smaller = sol1, sol2
        else:
            larger, smaller = sol2, sol1
        
        ask_for_larger = random.choice([True, False])
        
        if ask_for_larger:
            target_sol = larger
            direction = "較大"
        else:
            target_sol = smaller
            direction = "較小"
        
        expr = format_linear_expression(a, b)
        question_text = f"解絕對值方程式：|{expr}| = {c}\n\n請求出 {direction} 的解。"
        context_string = f"解絕對值方程式 |{expr}| = {c}，求{direction}的解"
        
        return {
            "question_text": question_text,
            "answer": str(target_sol),
            "correct_answer": str(target_sol),
            "context_string": context_string
        }
    
    else:  # linear_abs_any
        # |ax + b| = c，求所有解（圖形題，兩個答案）
        a = random.choice([1, -1, 2, -2, 3, -3])
        b = random.randint(-5, 5)
        c = random.randint(1, 8)
        
        # 計算兩個解（用於 context_string 給 AI 參考）
        sol1 = (c - b) / a
        sol2 = (-c - b) / a
        
        # 簡化顯示
        if sol1 == int(sol1):
            sol1 = int(sol1)
        else:
            sol1 = round(sol1, 2)
        if sol2 == int(sol2):
            sol2 = int(sol2)
        else:
            sol2 = round(sol2, 2)
        
        # 確保 sol1 和 sol2 不同
        if abs(sol1 - sol2) < 0.01:
            # 如果相同，重新生成
            return generate()
        
        expr = format_linear_expression(a, b)
        question_text = (
            f"請在下方的「數位計算紙」上，解絕對值方程式：|{expr}| = {c}\n\n"
            f"請在數線上標示出所有解，畫完後，請點擊「AI 檢查」按鈕。"
        )
        context_string = f"解絕對值方程式 |{expr}| = {c}，在數線上標示所有解（應有兩個解：{sol1} 和 {sol2}）"
        
        return {
            "question_text": question_text,
            "answer": None,
            "correct_answer": "graph",
            "context_string": context_string
        }

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer is None:
        return {"correct": False, "result": "系統錯誤：缺少正確答案"}
    
    # 處理圖形題（有兩個答案或以上的題目）
    if correct_answer == "graph":
        return {
            "correct": False,
            "result": "請使用畫筆在數線上標示所有解，然後點選「AI 檢查」",
            "next_question": False
        }
    
    user = user_answer.strip()
    
    # 處理單一答案的情況
    correct = str(correct_answer).strip()
    
    try:
        user_num = float(user)
        correct_num = float(correct)
        if abs(user_num - correct_num) < 0.01:  # 允許小數誤差
            return {"correct": True, "result": "正確！"}
        else:
            return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}
    except ValueError:
        return {"correct": False, "result": f"錯誤，請輸入數字。正解：{correct_answer}"}
