import random
from fractions import Fraction

def generate(level=1):
    """
    生成一道「條件機率」的題目。
    P(A|B) = P(A∩B) / P(B)
    """
    if level == 1:
        p_B = Fraction(random.randint(4, 7), 10)
        p_AnB = Fraction(random.randint(1, 3), 10)
        question_text = f"已知 P(B) = {p_B}，P(A∩B) = {p_AnB}，請求出條件機率 P(A|B)。(請以最簡分數 a/b 表示)"
        ans = p_AnB / p_B
    else: # level 2
        total = 52
        question_text = "從一副 52 張的撲克牌中抽出一張。已知抽出的牌是紅色的，請問這張牌是 K 的機率是多少？(請以最簡分數 a/b 表示)"
        # P(K | Red) = P(K and Red) / P(Red) = (2/52) / (26/52)
        ans = Fraction(2, 26)
    correct_answer = f"{ans.numerator}/{ans.denominator}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}