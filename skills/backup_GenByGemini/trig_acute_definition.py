import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「銳角三角函數定義」的題目。
    """
    # 使用畢氏三元數
    a, b, c = random.choice([(3,4,5), (5,12,13), (8,15,17)])
    
    func = random.choice(['sin', 'cos', 'tan'])
    
    question_text = f"在一個直角三角形中，兩股長為 {a} 和 {b}，斜邊長為 {c}。若其中一銳角為 θ，且其對邊長為 {a}，鄰邊長為 {b}，請問 {func}(θ) 的值是多少？ (請以最簡分數 a/b 表示)"
    
    if func == 'sin': # 對/斜
        frac = Fraction(a, c)
    elif func == 'cos': # 鄰/斜
        frac = Fraction(b, c)
    else: # tan, 對/鄰
        frac = Fraction(a, b)
        
    correct_answer = f"{frac.numerator}/{frac.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}