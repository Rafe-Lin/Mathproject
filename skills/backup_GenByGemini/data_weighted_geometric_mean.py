import random
import math

def generate(level=1):
    """
    生成一道「加權平均數與幾何平均數」的題目。
    level 1: 加權平均數。
    level 2: 幾何平均數。
    """
    if level == 1:
        w1, s1 = 3, random.randint(70, 90)
        w2, s2 = 2, random.randint(60, 80)
        w3, s3 = 1, random.randint(80, 100)
        question_text = f"某次月考，國文、英文、數學的學分數分別為 {w1}, {w2}, {w3}。若小明三科成績分別為 {s1}, {s2}, {s3} 分，請問他的加權平均分數是多少？"
        avg = (w1*s1 + w2*s2 + w3*s3) / (w1+w2+w3)
        correct_answer = str(round(avg, 1))
    else: # level 2
        r1 = random.randint(1, 5) # 2% -> 1.02
        r2 = random.randint(6, 10) # 7% -> 1.07
        question_text = f"某產品第一年的成長率為 {r1}%，第二年的成長率為 {r2}%，請問這兩年的平均成長率約為多少？ (使用幾何平均數，四捨五入至小數點後兩位)%"
        avg_rate = (math.sqrt((1 + r1/100) * (1 + r2/100)) - 1) * 100
        correct_answer = str(round(avg_rate, 2))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("%","")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}