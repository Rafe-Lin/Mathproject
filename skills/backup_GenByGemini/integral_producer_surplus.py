# \積分應用\生產者剩餘
import random

def generate(level=1):
    """
    生成一道「生產者剩餘」的題目。
    """
    # 供給曲線 S(x) = a + bx
    a = random.randint(10, 20)
    b = random.randint(2, 5)
    # 均衡數量 x₀
    x0 = random.randint(5, 10)
    # 均衡價格 p₀ = S(x₀)
    p0 = a + b * x0
    
    question_text = f"假設市場的供給函數為 S(x) = {a} + {b}x，當市場價格為 p₀ = {p0} 時，請問此時的「生產者剩餘」是多少？"
    # PS = ∫[0,x₀] (p₀ - S(x)) dx = ∫[0,x₀] ((a+bx₀) - (a+bx)) dx = ∫[0,x₀] b(x₀-x) dx
    # = b * [x₀x - x²/2] from 0 to x₀ = b * (x₀² - x₀²/2) = 1/2 * b * x₀²
    ans = 0.5 * b * x0**2
    correct_answer = str(ans)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}