import random

def generate(level=1):
    """
    生成一道「邊際意涵 (微分)」的題目。
    """
    if level == 1:
        question_text = (
            "在經濟學中，若 C(x) 為生產 x 件產品的成本函數，則「邊際成本」函數 C'(x) 代表什麼？\n\n"
            "A) 生產 x 件產品的總成本\n"
            "B) 每件產品的平均成本\n"
            "C) 每多生產一件產品時，成本的瞬時變化率"
        )
        correct_answer = "C"
    else: # level 2
        a, b, c = random.randint(1, 5), random.randint(10, 20), random.randint(50, 100)
        question_text = f"已知某產品的成本函數為 C(x) = {a}x² + {b}x + {c}，請問其邊際成本函數 C'(x) 為何？"
        correct_answer = f"{2*a}x + {b}"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").upper()
    correct = str(correct_answer).strip().replace(" ", "").upper()
    is_correct = (user == correct)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}