# \極限\介值定理
import random

def generate(level=1):
    """
    生成一道「介值定理(勘根定理)」的觀念題。
    """
    a, b = random.randint(1, 3), random.randint(4, 6)
    fa = random.randint(-10, -1)
    fb = random.randint(1, 10)
    
    if level == 1:
        question_text = f"已知連續函數 f(x) 在閉區間 [{a}, {b}] 上，f({a}) = {fa} 且 f({b}) = {fb}。請問在此區間內，方程式 f(x) = 0 是否「必定」有實根？ (是/否)"
        correct_answer = "是"
    else: # level 2
        question_text = f"已知多項式函數 f(x) 滿足 f({a}) = {fa} 且 f({b}) = {fb}。請問在區間 ({a}, {b}) 內，f(x) = 0 「至少」有幾個實根？"
        correct_answer = "1"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    correct = str(correct_answer).strip().upper()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}