import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「貝氏定理」的題目。
    """
    # 假設有兩家工廠 A, B 生產產品
    p_A = Fraction(random.randint(6, 7), 10) # A廠產量佔比
    p_B = 1 - p_A
    p_defect_given_A = Fraction(random.randint(1, 3), 100) # A廠不良率
    p_defect_given_B = Fraction(random.randint(4, 6), 100) # B廠不良率
    
    question_text = f"某產品由 A, B 兩家工廠生產，A 廠產量佔 {p_A}，B 廠佔 {p_B}。A 廠的不良率為 {p_defect_given_A}，B 廠的不良率為 {p_defect_given_B}。" \
                    "今在市場上隨機抽取一件產品，發現為不良品，請問此不良品來自 A 廠的機率是多少？ (請以最簡分數 a/b 表示)"
    
    # P(A|Defect) = P(A and Defect) / P(Defect)
    # P(A and Defect) = P(Defect|A) * P(A)
    p_A_and_defect = p_defect_given_A * p_A
    # P(Defect) = P(Defect|A)P(A) + P(Defect|B)P(B)
    p_defect = p_defect_given_A * p_A + p_defect_given_B * p_B
    ans = p_A_and_defect / p_defect
    correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}