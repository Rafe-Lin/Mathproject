import random

def generate(level=1):
    """
    生成一道「三集合取捨原理」的應用題。
    |A∪B∪C| = |A|+|B|+|C| - (|A∩B|+|A∩C|+|B∩C|) + |A∩B∩C|
    """
    total = random.randint(80, 100)
    A = random.randint(30, 40)
    B = random.randint(30, 40)
    C = random.randint(30, 40)
    AnB = random.randint(10, 15)
    AnC = random.randint(10, 15)
    BnC = random.randint(10, 15)
    AnBnC = random.randint(3, 8)

    if level == 1:
        question_text = f"某次調查，對 {total} 人進行問卷，喜歡 A 牌的有 {A} 人，喜歡 B 牌的有 {B} 人，喜歡 C 牌的有 {C} 人；三者都喜歡的有 {AnBnC} 人；只喜歡 A,B 的有 {AnB-AnBnC} 人，只喜歡 A,C 的有 {AnC-AnBnC} 人，只喜歡 B,C 的有 {BnC-AnBnC} 人。請問 A,B,C 至少喜歡一種的有幾人？"
        # |A∪B∪C|
        correct_answer = str(A + B + C - AnB - AnC - BnC + AnBnC)
    else: # level 2
        question_text = f"某次調查，對 {total} 人進行問卷，喜歡 A 牌的有 {A} 人，B 牌 {B} 人，C 牌 {C} 人；A,B皆喜歡者 {AnB} 人，A,C皆喜歡者 {AnC} 人，B,C皆喜歡者 {BnC} 人；三者都喜歡的有 {AnBnC} 人。請問三者皆不喜歡的有幾人？"
        # total - |A∪B∪C|
        union_val = A + B + C - AnB - AnC - BnC + AnBnC
        correct_answer = str(total - union_val)

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}