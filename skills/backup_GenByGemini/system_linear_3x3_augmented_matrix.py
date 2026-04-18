import random

def generate(level=1):
    """
    生成一道「增廣矩陣」的題目。
    """
    A = [[random.randint(1,9) for _ in range(3)] for _ in range(3)]
    B = [random.randint(1,9) for _ in range(3)]
    
    eq1 = f"{A[0][0]}x + {A[0][1]}y + {A[0][2]}z = {B[0]}"
    eq2 = f"{A[1][0]}x + {A[1][1]}y + {A[1][2]}z = {B[1]}"
    eq3 = f"{A[2][0]}x + {A[2][1]}y + {A[2][2]}z = {B[2]}"
    
    question_text = f"請寫出下列聯立方程式的增廣矩陣：\n{eq1}\n{eq2}\n{eq3}\n(這是一道觀念題，請在紙上作答)"
    correct_answer = "觀念題"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return {
        "correct": True, 
        "result": "觀念正確！增廣矩陣是將係數矩陣與常數項矩陣合併而成的。", 
        "next_question": True
    }